def calculate_ticket_cost(
    sensitivity_level: str,
    provider: str,
    actual_cost_usd: float = 0.0
) -> dict:
    """Calculate the actual cost, baseline cloud cost, and cost saved for a single transaction."""
    
    # 1. Determine baseline cost (what it would cost if sent to secure cloud)
    if sensitivity_level in ("high", "medium"):
        baseline_cost = 0.050  # Compliance secure cloud baseline
    else:
        baseline_cost = 0.003  # Standard standard cloud baseline

    # 2. Determine actual cost based on routing path
    if provider == "ollama" or provider == "degraded_local":
        actual_cost = 0.0
    else:
        actual_cost = actual_cost_usd

    # 3. Calculate savings
    savings = max(0.0, baseline_cost - actual_cost)

    return {
        "baseline_cost_usd": baseline_cost,
        "actual_cost_usd": actual_cost,
        "cost_saved_usd": round(savings, 5)
    }
