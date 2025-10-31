"""
Risk Predictor Tool
Predicts project risks using ML models and historical data
"""
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from .base import BaseTool, ToolParameter, ToolParameterType, ToolResult


class RiskPredictorTool(BaseTool):
    """Predicts project risks using ML and pattern analysis"""
    
    name = "predict_risk"
    description = "Predicts project risks based on historical data and current metrics"
    category = "prediction"
    version = "1.0.0"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.ml_service_url = config.get("ml_service_url") if config else None
    
    def get_parameters(self) -> Dict[str, ToolParameter]:
        return {
            "project_key": ToolParameter(
                type=ToolParameterType.STRING,
                description="Project identifier",
                required=True
            ),
            "component_name": ToolParameter(
                type=ToolParameterType.STRING,
                description="Specific component or module to analyze",
                required=False
            ),
            "prediction_horizon_days": ToolParameter(
                type=ToolParameterType.INTEGER,
                description="Days ahead to predict (default: 30)",
                required=False,
                default=30
            ),
            "include_recommendations": ToolParameter(
                type=ToolParameterType.BOOLEAN,
                description="Include risk mitigation recommendations",
                required=False,
                default=True
            )
        }
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute risk prediction
        
        Args:
            parameters: Tool parameters including project_key
            
        Returns:
            ToolResult with risk predictions
        """
        try:
            project_key = parameters["project_key"]
            component = parameters.get("component_name")
            horizon = parameters.get("prediction_horizon_days", 30)
            include_recs = parameters.get("include_recommendations", True)
            
            # Check if ML service is available
            if self.ml_service_url:
                prediction = await self._ml_prediction(
                    project_key, component, horizon
                )
            else:
                prediction = self._heuristic_prediction(
                    project_key, component, horizon
                )
            
            # Add recommendations if requested
            if include_recs:
                prediction["recommendations"] = self._generate_recommendations(
                    prediction
                )
            
            return ToolResult(
                success=True,
                data=prediction,
                metadata={
                    "project_key": project_key,
                    "component": component,
                    "prediction_horizon_days": horizon,
                    "predicted_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Risk prediction failed: {str(e)}"
            )
    
    async def _ml_prediction(
        self, 
        project_key: str, 
        component: Optional[str], 
        horizon: int
    ) -> Dict[str, Any]:
        """Use ML service for prediction"""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ml_service_url}/predict-risk",
                json={
                    "project_key": project_key,
                    "component": component,
                    "horizon_days": horizon
                }
            )
            response.raise_for_status()
            return response.json()
    
    def _heuristic_prediction(
        self, 
        project_key: str, 
        component: Optional[str], 
        horizon: int
    ) -> Dict[str, Any]:
        """Heuristic-based risk prediction when ML service unavailable"""
        
        # Mock risk factors (in production, fetch from database)
        risk_factors = {
            "velocity_trend": "declining",
            "blocker_count": 5,
            "high_priority_percentage": 35,
            "team_capacity": 85,
            "code_quality_score": 72,
            "test_coverage": 68
        }
        
        # Calculate risk scores
        schedule_risk = self._calculate_schedule_risk(risk_factors)
        quality_risk = self._calculate_quality_risk(risk_factors)
        resource_risk = self._calculate_resource_risk(risk_factors)
        
        # Overall risk
        overall_risk = (schedule_risk + quality_risk + resource_risk) / 3
        
        return {
            "overall_risk_score": round(overall_risk, 2),
            "risk_level": self._risk_level_from_score(overall_risk),
            "risk_breakdown": {
                "schedule_risk": {
                    "score": round(schedule_risk, 2),
                    "level": self._risk_level_from_score(schedule_risk),
                    "factors": ["Declining velocity", "High blocker count"]
                },
                "quality_risk": {
                    "score": round(quality_risk, 2),
                    "level": self._risk_level_from_score(quality_risk),
                    "factors": ["Below target test coverage", "Moderate code quality"]
                },
                "resource_risk": {
                    "score": round(resource_risk, 2),
                    "level": self._risk_level_from_score(resource_risk),
                    "factors": ["High team capacity utilization"]
                }
            },
            "predicted_issues": {
                "likely_delays_days": 5 if schedule_risk > 60 else 0,
                "potential_quality_defects": 8 if quality_risk > 60 else 3,
                "resource_shortfall_percentage": 15 if resource_risk > 70 else 0
            },
            "confidence": 0.75,
            "prediction_method": "heuristic",
            "note": "Using heuristic model - ML service not available"
        }
    
    def _calculate_schedule_risk(self, factors: Dict[str, Any]) -> float:
        """Calculate schedule risk score (0-100)"""
        risk_score = 30.0  # Base risk
        
        if factors["velocity_trend"] == "declining":
            risk_score += 25
        
        risk_score += min(factors["blocker_count"] * 5, 25)
        
        if factors["high_priority_percentage"] > 30:
            risk_score += 20
        
        return min(100, risk_score)
    
    def _calculate_quality_risk(self, factors: Dict[str, Any]) -> float:
        """Calculate quality risk score (0-100)"""
        risk_score = 20.0  # Base risk
        
        if factors["code_quality_score"] < 80:
            risk_score += (80 - factors["code_quality_score"]) * 0.5
        
        if factors["test_coverage"] < 80:
            risk_score += (80 - factors["test_coverage"]) * 0.5
        
        return min(100, risk_score)
    
    def _calculate_resource_risk(self, factors: Dict[str, Any]) -> float:
        """Calculate resource risk score (0-100)"""
        risk_score = 15.0  # Base risk
        
        if factors["team_capacity"] > 90:
            risk_score += 40
        elif factors["team_capacity"] > 80:
            risk_score += 25
        elif factors["team_capacity"] > 70:
            risk_score += 10
        
        return min(100, risk_score)
    
    def _risk_level_from_score(self, score: float) -> str:
        """Convert risk score to level"""
        if score >= 75:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, prediction: Dict[str, Any]) -> list:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        risk_breakdown = prediction.get("risk_breakdown", {})
        
        # Schedule risk recommendations
        if risk_breakdown.get("schedule_risk", {}).get("score", 0) > 60:
            recommendations.append({
                "category": "schedule",
                "priority": "high",
                "action": "Address blockers immediately",
                "details": "Focus on removing the top blocking issues to improve velocity"
            })
            recommendations.append({
                "category": "schedule",
                "priority": "medium",
                "action": "Re-evaluate sprint commitments",
                "details": "Consider reducing scope or extending timeline"
            })
        
        # Quality risk recommendations
        if risk_breakdown.get("quality_risk", {}).get("score", 0) > 60:
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "action": "Increase test coverage",
                "details": "Target 80%+ code coverage for critical paths"
            })
            recommendations.append({
                "category": "quality",
                "priority": "medium",
                "action": "Schedule code review sessions",
                "details": "Implement stricter code review process"
            })
        
        # Resource risk recommendations
        if risk_breakdown.get("resource_risk", {}).get("score", 0) > 70:
            recommendations.append({
                "category": "resource",
                "priority": "high",
                "action": "Allocate additional resources",
                "details": "Team is at high capacity - consider adding team members or reducing workload"
            })
        
        return recommendations
