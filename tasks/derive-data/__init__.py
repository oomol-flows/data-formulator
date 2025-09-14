#region generated meta
import typing
from oocana import LLMModelOptions
class Inputs(typing.TypedDict):
    data: list[dict]
    instruction: str
    x_axis_name: str | None
    y_axis_name: str | None
    code_repair_attempts: int | None
    llm_model: LLMModelOptions
class Outputs(typing.TypedDict):
    code_for_derive: str
    code_explain: str
    content: list[dict]
    refined_x_axis_name: str
    refined_y_axis_name: str
#endregion

import logging
from typing import Any, Dict, List, Optional, Tuple

from data_formulator.agents.agent_code_explanation import CodeExplanationAgent
from data_formulator.agents.agent_data_transform_v2 import DataTransformationAgentV2
from data_formulator.agents.client_utils import Client
from oocana import Context

# Configure logging
logger = logging.getLogger(__name__)

def _validate_inputs(params: Inputs) -> None:
    """Validate input parameters with enhanced checks"""
    # Check data presence and format
    data = params.get("data")
    if not data:
        raise ValueError("No data provided. Please provide input dataset.")

    if not isinstance(data, list):
        raise ValueError(f"Invalid data format. Expected list, got {type(data).__name__}")

    # Validate data structure
    for i, table in enumerate(data):
        if not isinstance(table, dict):
            raise ValueError(f"Invalid table format at index {i}. Expected dict, got {type(table).__name__}")

        if "name" not in table:
            raise ValueError(f"Table at index {i} missing required 'name' field")

        if "rows" not in table:
            raise ValueError(f"Table at index {i} missing required 'rows' field")

    # Check instruction
    instruction = params.get("instruction")
    if not instruction or not instruction.strip():
        raise ValueError("No instruction provided. Please describe the data transformation to perform.")

    # Validate code repair attempts if provided
    repair_attempts = params.get("code_repair_attempts")
    if repair_attempts is not None and (not isinstance(repair_attempts, int) or repair_attempts < 1):
        raise ValueError("code_repair_attempts must be a positive integer")

    # Validate LLM model configuration
    llm_model = params.get("llm_model", {})
    if not isinstance(llm_model, dict):
        raise ValueError("Invalid LLM model configuration format")

    logger.info(f"Input validation successful: {len(data)} tables, instruction length: {len(instruction)}")

def _create_llm_client(params: Inputs, context: Context) -> Client:
    """Create LLM client with validation"""
    try:
        llm_model = params.get("llm_model", {})

        # Validate environment configuration
        if not context.oomol_llm_env.get("api_key"):
            raise ValueError("LLM API key not found in environment")

        if not context.oomol_llm_env.get("base_url_v1"):
            raise ValueError("LLM base URL not found in environment")

        model_name = llm_model.get("model", "oomol-chat")
        logger.info(f"Creating LLM client with model: {model_name}")

        client = Client(
            endpoint="openai",
            api_base=context.oomol_llm_env.get("base_url_v1"),
            model=model_name,
            api_key=context.oomol_llm_env.get("api_key")
        )

        return client
    except Exception as e:
        raise RuntimeError(f"Failed to create LLM client: {str(e)}")

def _process_data_with_repair(
    agent: DataTransformationAgentV2,
    input_tables: List[Dict[str, Any]],
    instruction: str,
    expected_fields: List[str],
    max_attempts: int
) -> Dict[str, Any]:
    """Process data transformation with automatic error repair"""
    logger.info(f"Starting data transformation with max {max_attempts} repair attempts")

    try:
        # Initial transformation attempt
        results = agent.run(input_tables, instruction, expected_fields, [], max_attempts)

        if not results or len(results) == 0:
            raise RuntimeError("No results returned from data transformation agent")

        result = results[0]
        repair_attempts = 0

        while result.get('status') == 'error' and repair_attempts < max_attempts:
            error_message = result.get('content', 'Unknown error')
            logger.warning(f"Code generation failed (attempt {repair_attempts + 1}): {error_message}")

            # Create repair instruction
            repair_instruction = (
                f"The following error occurred during code execution:\n\n{error_message}\n\n"
                "Please analyze the error and fix the code to prevent similar issues. "
                "Focus on data type compatibility, column name accuracy, and proper error handling."
            )

            prev_dialog = result.get('dialog', [])
            if not prev_dialog:
                logger.error("No dialog history available for repair")
                break

            # Attempt repair
            logger.info(f"Attempting code repair (attempt {repair_attempts + 1})")
            repair_results = agent.followup(input_tables, prev_dialog, expected_fields, repair_instruction)

            if not repair_results or len(repair_results) == 0:
                logger.error("No results returned from repair attempt")
                break

            result = repair_results[0]
            repair_attempts += 1

        if result.get('status') == 'error':
            final_error = result.get('content', 'Unknown error')
            raise RuntimeError(
                f"Failed to generate valid code after {max_attempts} repair attempts. "
                f"Final error: {final_error}"
            )

        logger.info("Data transformation completed successfully")
        return result

    except Exception as e:
        logger.error(f"Data transformation failed: {str(e)}")
        raise RuntimeError(f"Data processing failed: {str(e)}")

def _determine_axis_names(
    result: Dict[str, Any],
    x_axis_name: Optional[str],
    y_axis_name: Optional[str]
) -> Tuple[str, str]:
    """Determine axis names with improved logic and caching"""
    # Cache frequently accessed values
    refined_goal = result.get('refined_goal', {})
    visualization_fields = refined_goal.get('visualization_fields', [])
    content = result.get('content', [])

    # Get available columns from data
    available_columns = []
    if content and isinstance(content, list) and len(content) > 0:
        first_row = content[0]
        if isinstance(first_row, dict):
            available_columns = list(first_row.keys())

    logger.info(f"Available columns: {available_columns}")
    logger.info(f"Visualization fields: {visualization_fields}")

    # Determine X-axis name with priority order
    refined_x = (
        x_axis_name or  # User-specified name
        (visualization_fields[0] if visualization_fields else None) or  # From refined goal
        (available_columns[0] if available_columns else None) or  # First available column
        "index"  # Default fallback
    )

    # Determine Y-axis name with priority order
    refined_y = (
        y_axis_name or  # User-specified name
        (visualization_fields[1] if len(visualization_fields) >= 2 else None) or  # Second visualization field
        (available_columns[1] if len(available_columns) >= 2 else None) or  # Second available column
        "count"  # Default fallback
    )

    logger.info(f"Determined axis names - X: '{refined_x}', Y: '{refined_y}'")
    return refined_x, refined_y

def main(params: Inputs, context: Context) -> Outputs:
    """Main function to process data transformation with comprehensive error handling"""
    logger.info("Starting derive-data task execution")

    try:
        # Validate input parameters
        _validate_inputs(params)

        # Extract parameters with defaults
        input_tables = params["data"]
        instruction = params["instruction"]
        max_repair_attempts = params.get("code_repair_attempts", 3)
        x_axis_name = params.get("x_axis_name")
        y_axis_name = params.get("y_axis_name")

        logger.info(f"Processing {len(input_tables)} tables with instruction: {instruction[:100]}...")

        # Create LLM client
        llm_client = _create_llm_client(params, context)

        # Build expected fields list (filter out None values)
        expected_fields = [name for name in [x_axis_name, y_axis_name] if name is not None]
        logger.info(f"Expected fields for visualization: {expected_fields}")

        # Create data transformation agent and process
        logger.info("Creating data transformation agent")
        agent = DataTransformationAgentV2(client=llm_client)

        # Process data with automatic repair
        result = _process_data_with_repair(
            agent, input_tables, instruction, expected_fields, max_repair_attempts
        )

        # Extract results with validation
        code = result.get('code')
        content = result.get('content')

        if not code:
            raise RuntimeError("No transformation code generated")

        if content is None:
            raise RuntimeError("No transformed content generated")

        logger.info(f"Generated code length: {len(code)} characters")
        logger.info(f"Transformed data rows: {len(content) if isinstance(content, list) else 'N/A'}")

        # Determine axis names
        refined_x_axis_name, refined_y_axis_name = _determine_axis_names(result, x_axis_name, y_axis_name)

        # Generate code explanation
        logger.info("Generating code explanation")
        try:
            code_expl_agent = CodeExplanationAgent(client=llm_client)
            code_explain = code_expl_agent.run(input_tables, code)
        except Exception as e:
            logger.warning(f"Failed to generate code explanation: {str(e)}")
            code_explain = f"Code explanation generation failed: {str(e)}"

        logger.info("Data transformation task completed successfully")

        return {
            "code_for_derive": code,
            "code_explain": code_explain,
            "content": content,
            "refined_x_axis_name": refined_x_axis_name,
            "refined_y_axis_name": refined_y_axis_name
        }

    except ValueError as e:
        logger.error(f"Input validation error: {str(e)}")
        raise ValueError(str(e))
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        raise RuntimeError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error in derive-data task: {str(e)}")
        raise RuntimeError(f"Data derivation failed: {str(e)}") 