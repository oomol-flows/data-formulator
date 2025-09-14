#region generated meta
import typing
class Inputs(typing.TypedDict):
    file_name: str
    data_rows: list[dict]
    sample_size: int | None
class Outputs(typing.TypedDict):
    summary: str
    fields_schema: list[dict]
    statistics: dict
#endregion

import random
from typing import Dict, List, Any, Optional
from oocana.preview import TextPreviewPayload
from data_formulator.agents.agent_data_load import DataLoadAgent
from data_formulator.agents.client_utils import Client
from oocana import Context


class DataSummarizerError(Exception):
    """Custom exception for data summarizer errors"""
    pass


class InputValidationError(DataSummarizerError):
    """Raised when input validation fails"""
    pass


class LLMClientError(DataSummarizerError):
    """Raised when LLM client operations fail"""
    pass


def validate_inputs(params: Inputs) -> None:
    """Validate input parameters"""
    file_name = params.get("file_name")
    if not file_name or not file_name.strip():
        raise InputValidationError("File name is required and cannot be empty")

    data_rows = params.get("data_rows", [])
    if not data_rows or len(data_rows) == 0:
        raise InputValidationError("No data rows provided")

    # Validate data structure
    if not all(isinstance(row, dict) for row in data_rows):
        raise InputValidationError("All data rows must be dictionary objects")


def sample_data(data_rows: List[Dict], sample_size: Optional[int]) -> List[Dict]:
    """Sample data for large datasets to improve performance"""
    if not sample_size or len(data_rows) <= sample_size:
        return data_rows

    # Use random sampling for large datasets
    return random.sample(data_rows, sample_size)


def calculate_basic_statistics(data_rows: List[Dict]) -> Dict[str, Any]:
    """Calculate basic statistical information about the dataset"""
    if not data_rows:
        return {}

    total_rows = len(data_rows)
    total_columns = len(data_rows[0].keys()) if data_rows else 0

    # Analyze data types and null values
    column_stats = {}
    for column in data_rows[0].keys():
        values = [row.get(column) for row in data_rows]
        non_null_values = [v for v in values if v is not None and v != ""]

        column_stats[column] = {
            "total_values": len(values),
            "non_null_values": len(non_null_values),
            "null_percentage": round((len(values) - len(non_null_values)) / len(values) * 100, 2),
            "unique_values": len(set(str(v) for v in non_null_values)) if non_null_values else 0
        }

    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "columns": list(data_rows[0].keys()) if data_rows else [],
        "column_statistics": column_stats
    }


def create_llm_client(context: Context) -> Client:
    """Create and configure LLM client"""
    try:
        if not context.oomol_llm_env:
            raise LLMClientError("LLM environment configuration is not available")

        api_base = context.oomol_llm_env.get("base_url_v1")
        api_key = context.oomol_llm_env.get("api_key")

        if not api_base or not api_key:
            raise LLMClientError("LLM API configuration is incomplete")

        return Client(
            endpoint="openai",
            api_base=api_base,
            model="oomol-chat",
            api_key=api_key
        )
    except Exception as e:
        raise LLMClientError(f"Failed to create LLM client: {str(e)}")


def analyze_data_with_ai(data_rows: List[Dict], file_name: str, llm_client: Client, context: Context) -> Dict[str, Any]:
    """Analyze data using AI agent"""
    try:
        agent = DataLoadAgent(client=llm_client, logger=context.logger)
        candidates = agent.run(input_data={
            "name": file_name,
            "rows": data_rows
        })

        # Filter successful results
        valid_candidates = [c['content'] for c in candidates if c.get('status') == 'ok']

        if not valid_candidates:
            raise DataSummarizerError("AI analysis failed - no valid results obtained")

        return valid_candidates[0]

    except Exception as e:
        raise DataSummarizerError(f"AI analysis failed: {str(e)}")


def format_summary(ai_result: Dict[str, Any], statistics: Dict[str, Any]) -> str:
    """Format the summary with AI insights and statistics"""
    summary_parts = []

    # Add AI-generated summary
    ai_summary = ai_result.get("data summary", "")
    if ai_summary:
        summary_parts.append(f"## Data Insights\n\n{ai_summary}")

    # Add basic statistics
    stats = statistics
    if stats:
        summary_parts.append(f"\n## Dataset Overview\n\n")
        summary_parts.append(f"- **Total Rows**: {stats.get('total_rows', 'N/A')}")
        summary_parts.append(f"- **Total Columns**: {stats.get('total_columns', 'N/A')}")

        if stats.get('columns'):
            summary_parts.append(f"- **Columns**: {', '.join(stats['columns'])}")

    return "\n".join(summary_parts)


def preview_result(context: Context, summary: str, error: bool = False) -> None:
    """Preview the result or error message"""
    try:
        if error:
            content = f"**Error**: {summary}"
        else:
            content = summary

        context.preview(TextPreviewPayload(
            type="markdown",
            data=content
        ))
    except Exception as preview_error:
        context.logger.warning(f"Preview failed: {str(preview_error)}")


def main(params: Inputs, context: Context) -> Outputs:
    """Main function to generate data summary with AI-powered analysis"""
    try:
        # Validate inputs
        validate_inputs(params)

        file_name = params["file_name"]
        data_rows = params["data_rows"]
        sample_size = params.get("sample_size")

        # Sample data if needed for performance
        sampled_data = sample_data(data_rows, sample_size)
        if len(sampled_data) < len(data_rows):
            context.logger.info(f"Sampled {len(sampled_data)} rows from {len(data_rows)} total rows")

        # Calculate basic statistics
        statistics = calculate_basic_statistics(sampled_data)

        # Create LLM client
        llm_client = create_llm_client(context)

        # Analyze data with AI
        ai_result = analyze_data_with_ai(sampled_data, file_name, llm_client, context)

        # Extract results
        fields_schema = ai_result.get("fields", [])
        summary = format_summary(ai_result, statistics)

        # Preview result
        preview_result(context, summary)

        return {
            "summary": summary,
            "fields_schema": fields_schema,
            "statistics": statistics
        }

    except InputValidationError as e:
        error_msg = f"Input validation error: {str(e)}"
        context.logger.error(error_msg)
        preview_result(context, error_msg, error=True)
        raise ValueError(error_msg)

    except LLMClientError as e:
        error_msg = f"LLM client error: {str(e)}"
        context.logger.error(error_msg)
        preview_result(context, error_msg, error=True)
        raise RuntimeError(error_msg)

    except DataSummarizerError as e:
        error_msg = f"Data analysis error: {str(e)}"
        context.logger.error(error_msg)
        preview_result(context, error_msg, error=True)
        raise RuntimeError(error_msg)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        context.logger.error(error_msg)
        preview_result(context, error_msg, error=True)
        raise RuntimeError(error_msg)
