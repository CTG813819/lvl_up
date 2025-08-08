import pytest
import httpx

BASE_URL = "http://localhost:8000"  # Change to your EC2 public IP if needed

@pytest.mark.asyncio
async def test_training_ground_scenario():
    async with httpx.AsyncClient() as client:
        for diff in ['1', '2', '3']:
            resp = await client.post(f"{BASE_URL}/api/custody/training-ground/scenario", json={
                "sandbox_level": 10,
                "difficulty": diff
            })
            assert resp.status_code == 200
            data = resp.json()
            assert "scenario" in data
            assert "objectives" in data["scenario"]

@pytest.mark.asyncio
async def test_training_ground_deploy():
    async with httpx.AsyncClient() as client:
        scenario_resp = await client.post(f"{BASE_URL}/api/custody/training-ground/scenario", json={
            "sandbox_level": 10,
            "difficulty": "2"
        })
        scenario = scenario_resp.json()["scenario"]
        deploy_resp = await client.post(f"{BASE_URL}/api/custody/training-ground/deploy", json={
            "scenario": scenario,
            "user_id": "testuser"
        })
        assert deploy_resp.status_code == 200
        result = deploy_resp.json()["data"]
        assert "xp_awarded" in result
        assert "learning_awarded" in result
        assert "progress_details" in result

@pytest.mark.asyncio
async def test_olympics():
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{BASE_URL}/api/custody/olympics/run", json={
            "participants": ["imperium", "guardian"],
            "difficulty": "advanced",
            "event_type": "olympics"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data

@pytest.mark.asyncio
async def test_leaderboard():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/api/custody/leaderboard")
        assert resp.status_code == 200
        assert "data" in resp.json()

@pytest.mark.asyncio
async def test_explainability():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/api/custody/explainability-analytics")
        assert resp.status_code == 200
        assert "data" in resp.json()

@pytest.mark.asyncio
async def test_feedback_and_acceptance():
    # This is a placeholder; you need a real proposal_id to test
    proposal_id = "00000000-0000-0000-0000-000000000000"
    async with httpx.AsyncClient() as client:
        feedback_resp = await client.post(f"{BASE_URL}/api/proposals/{proposal_id}/feedback", json={
            "reviewer": "testuser",
            "feedback_type": "approval",
            "rating": 5,
            "comment": "Looks good!"
        })
        # Accept may fail if proposal_id is not real, but endpoint should exist
        accept_resp = await client.post(f"{BASE_URL}/api/proposals/{proposal_id}/accept")
        assert feedback_resp.status_code in [200, 404, 400]
        assert accept_resp.status_code in [200, 404, 400]

@pytest.mark.asyncio
async def test_scheduler():
    async with httpx.AsyncClient() as client:
        get_resp = await client.get(f"{BASE_URL}/api/ai/scheduler/all_intervals")
        assert get_resp.status_code == 200
        post_resp = await client.post(f"{BASE_URL}/api/ai/scheduler/all_intervals", json={
            "agent_scheduler_interval": 60,
            "github_monitor_interval": 60,
            "learning_cycle_interval": 60,
            "custody_testing_interval": 60
        })
        assert post_resp.status_code == 200

@pytest.mark.asyncio
async def test_error_handling():
    async with httpx.AsyncClient() as client:
        # Invalid AI type
        resp = await client.post(f"{BASE_URL}/api/custody/test/invalidai")
        assert resp.status_code == 400 or resp.status_code == 422
        # Invalid endpoint
        resp2 = await client.get(f"{BASE_URL}/api/custody/doesnotexist")
        assert resp2.status_code == 404 