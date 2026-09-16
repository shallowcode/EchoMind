"""Versioned, uncached list-price estimates; never a provider billing statement.

Source https://bigmodel.cn/pricing, checked 2026-09-08. GLM-4.5-Air has
per-call input AND output length tiers. Cache discounts and account credits are excluded.
"""


def estimate_call(settings, input_tokens, output_tokens):
    if settings.pricing_profile == "glm-air-20260908":
        if input_tokens >= 128000:
            return None
        inp, out = (
            (1.2, 8.0)
            if input_tokens >= 32000
            else (0.8, 2.0 if output_tokens < 200 else 6.0)
        )
    elif (
        settings.model_input_price is not None
        and settings.model_output_price is not None
    ):
        inp, out = settings.model_input_price, settings.model_output_price
    else:
        return None
    return (input_tokens * inp + output_tokens * out) / 1e6
