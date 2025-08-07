from datetime import datetime, timedelta
from typing import Dict, Any, List


class JarvisService:
    """Minimal Jarvis service providing development/status metrics.
    This can be replaced with real training/learning integration later.
    """

    def __init__(self) -> None:
        self._growth_score: float = 0.0
        self._last_learning_result: str = "idle"
        self._delta_growth: float = 0.0
        self._recent_knowledge: List[Dict[str, Any]] = []
        self._last_run: datetime | None = None
        self._status: str = "initializing"
        self._proposals_generated: int = 0

        # Seed with placeholder data
        self._bootstrap()

    def _bootstrap(self) -> None:
        self._growth_score = 12.5
        self._last_learning_result = "initialized"
        self._delta_growth = 0.5
        self._recent_knowledge = [
            {
                "source": "internet",
                "topic": "secure password rotation",
                "timestamp": datetime.utcnow().isoformat(),
            },
            {
                "source": "berserk",
                "topic": "weapon synthesis patterns",
                "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
            },
        ]
        self._last_run = datetime.utcnow() - timedelta(minutes=1)
        self._status = "active"
        self._proposals_generated = 2

    def trigger_learning_cycle(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        self._last_run = now
        self._last_learning_result = "success"
        self._delta_growth = 0.8
        self._growth_score += self._delta_growth
        self._proposals_generated += 1
        self._recent_knowledge.insert(
            0,
            {
                "source": "horus",
                "topic": "app generation heuristics",
                "timestamp": now.isoformat(),
            },
        )
        # Keep recent list short
        self._recent_knowledge = self._recent_knowledge[:10]
        return self.get_status()

    def integrate_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate development signals from Horus, Berserk, Chaos, Adversarial, and Internet.
        Expected keys: horus, berserk, chaos, adversarial, internet_digest (optional string)
        """
        now = datetime.utcnow()
        growth_delta = 0.0

        horus = signals.get("horus") or {}
        if horus:
            growth_delta += float(horus.get("average_complexity", 0.0)) * 0.05
            self._recent_knowledge.insert(0, {
                "source": "horus",
                "topic": f"weapons={horus.get('total_weapons', 0)} complexity={horus.get('average_complexity', 0)}",
                "timestamp": now.isoformat(),
            })

        berserk = signals.get("berserk") or {}
        if berserk:
            growth_delta += float(berserk.get("active_deployments", 0)) * 0.1
            self._recent_knowledge.insert(0, {
                "source": "berserk",
                "topic": f"systems_compromised={berserk.get('systems_compromised', 0)}",
                "timestamp": now.isoformat(),
            })

        chaos = signals.get("chaos") or {}
        if chaos:
            growth_delta += 0.05
            self._recent_knowledge.insert(0, {
                "source": "chaos",
                "topic": f"language_version={chaos.get('version', 'unknown')}",
                "timestamp": now.isoformat(),
            })

        adversarial = signals.get("adversarial") or {}
        if adversarial:
            success_rate = float(adversarial.get("overall_success_rate", 0.0))
            growth_delta += success_rate * 0.02
            self._recent_knowledge.insert(0, {
                "source": "adversarial",
                "topic": f"success_rate={success_rate}",
                "timestamp": now.isoformat(),
            })

        internet_digest = signals.get("internet_digest")
        if internet_digest:
            growth_delta += 0.1
            self._recent_knowledge.insert(0, {
                "source": "internet",
                "topic": internet_digest,
                "timestamp": now.isoformat(),
            })

        # Update core stats
        self._delta_growth = round(growth_delta, 3)
        self._growth_score = round(self._growth_score + self._delta_growth, 3)
        self._last_learning_result = "aggregated"
        self._last_run = now
        self._status = "active"
        # Keep recent list short
        self._recent_knowledge = self._recent_knowledge[:10]
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": self._status,
            "growth_score": round(self._growth_score, 3),
            "delta_growth": round(self._delta_growth, 3),
            "last_learning_result": self._last_learning_result,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "recent_knowledge": self._recent_knowledge,
            "proposals_generated": self._proposals_generated,
        }


# Singleton
jarvis_service = JarvisService()
