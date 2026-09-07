from core.planner.service import DeterministicPlannerProvider, Planner


def test_planner_uses_deterministic_provider_by_default(monkeypatch):
    monkeypatch.delenv("V_AGENT_LLM_ENABLED", raising=False)
    assert isinstance(Planner().provider, DeterministicPlannerProvider)


def test_planner_does_not_enable_llm_from_api_key_only(monkeypatch):
    monkeypatch.delenv("V_AGENT_LLM_ENABLED", raising=False)
    monkeypatch.setenv("V_AGENT_LLM_API_KEY", "present")
    assert isinstance(Planner().provider, DeterministicPlannerProvider)
