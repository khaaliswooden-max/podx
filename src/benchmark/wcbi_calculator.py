"""
WCBI (Weighted Composite Benchmark Index) Calculator
=====================================================

Calculates the overall XdoP compliance score based on weighted domain scores.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WCBIResult:
    """Result of WCBI calculation."""
    total_score: float
    domain_scores: Dict[str, float]
    weighted_contributions: Dict[str, float]
    level_3_compliant: bool
    min_domain_score: float
    weakest_domain: str


class WCBICalculator:
    """
    Calculator for Weighted Composite Benchmark Index (WCBI).
    
    The WCBI is calculated as the sum of weighted domain scores:
    WCBI = Σ(domain_score × domain_weight)
    
    For Level 3 Mission Critical certification:
    - Overall WCBI must be ≥85
    - Each individual domain must score ≥80
    """
    
    # Standard domain weights
    WEIGHTS = {
        'mobility_network': 0.20,
        'energy_power': 0.18,
        'reliability': 0.17,
        'compute_performance': 0.15,
        'security_compliance': 0.12,
        'ruggedization': 0.10,
        'sustainability_tco': 0.08,
    }
    
    # Level 3 thresholds
    LEVEL_3_MIN_WCBI = 85
    LEVEL_3_MIN_DOMAIN = 80
    
    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """
        Initialize calculator with optional custom weights.
        
        Args:
            custom_weights: Optional dictionary of custom domain weights
        """
        self.weights = custom_weights or self.WEIGHTS.copy()
        
        # Validate weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.001:
            logger.warning(f"Weights sum to {total_weight}, normalizing to 1.0")
            for key in self.weights:
                self.weights[key] /= total_weight
    
    def calculate(self, domain_scores: Dict[str, float]) -> WCBIResult:
        """
        Calculate WCBI from domain scores.
        
        Args:
            domain_scores: Dictionary mapping domain names to scores (0-100)
            
        Returns:
            WCBIResult with total score and breakdown
        """
        weighted_contributions = {}
        total_score = 0.0
        
        for domain, weight in self.weights.items():
            score = domain_scores.get(domain, 0)
            contribution = score * weight
            weighted_contributions[domain] = contribution
            total_score += contribution
        
        # Find minimum domain score
        min_score = min(domain_scores.values()) if domain_scores else 0
        weakest_domain = min(domain_scores, key=domain_scores.get) if domain_scores else "N/A"
        
        # Check Level 3 compliance
        level_3_compliant = (
            total_score >= self.LEVEL_3_MIN_WCBI and
            min_score >= self.LEVEL_3_MIN_DOMAIN
        )
        
        return WCBIResult(
            total_score=total_score,
            domain_scores=domain_scores.copy(),
            weighted_contributions=weighted_contributions,
            level_3_compliant=level_3_compliant,
            min_domain_score=min_score,
            weakest_domain=weakest_domain,
        )
    
    def calculate_required_improvement(
        self,
        current_scores: Dict[str, float],
        target_wcbi: float = 85
    ) -> Dict[str, float]:
        """
        Calculate required improvement per domain to reach target WCBI.
        
        Args:
            current_scores: Current domain scores
            target_wcbi: Target WCBI score (default: 85 for Level 3)
            
        Returns:
            Dictionary of required score improvements per domain
        """
        current_result = self.calculate(current_scores)
        gap = target_wcbi - current_result.total_score
        
        if gap <= 0:
            return {domain: 0 for domain in self.weights}
        
        # Calculate improvement needed (proportional to weight)
        improvements = {}
        for domain, weight in self.weights.items():
            current = current_scores.get(domain, 0)
            headroom = 100 - current
            
            if headroom > 0:
                # Proportional improvement based on weight and headroom
                proportional_gap = gap * (weight / sum(self.weights.values()))
                needed = min(proportional_gap / weight, headroom)
                improvements[domain] = needed
            else:
                improvements[domain] = 0
        
        return improvements
    
    def generate_scorecard(self, result: WCBIResult) -> str:
        """
        Generate a formatted scorecard string.
        
        Args:
            result: WCBIResult to format
            
        Returns:
            Formatted scorecard string
        """
        lines = [
            "╔════════════════════════════════════════════════════════════╗",
            "║              XDOP WCBI SCORECARD                           ║",
            "╠════════════════════════════════════════════════════════════╣",
            "║ Domain                    │ Weight │ Score │ Contribution ║",
            "╠═══════════════════════════╪════════╪═══════╪══════════════╣",
        ]
        
        for domain, weight in self.weights.items():
            score = result.domain_scores.get(domain, 0)
            contrib = result.weighted_contributions.get(domain, 0)
            name = domain.replace('_', ' ').title()[:25].ljust(25)
            lines.append(
                f"║ {name} │ {weight*100:5.0f}% │ {score:5.1f} │ {contrib:11.2f} ║"
            )
        
        lines.extend([
            "╠═══════════════════════════╧════════╧═══════╧══════════════╣",
            f"║ TOTAL WCBI SCORE: {result.total_score:6.1f}/100                       ║",
            f"║ Level 3 Compliant: {'YES ✓' if result.level_3_compliant else 'NO ✗'}                              ║",
            "╚════════════════════════════════════════════════════════════╝",
        ])
        
        return "\n".join(lines)


def main():
    """Demo WCBI calculation."""
    calculator = WCBICalculator()
    
    # Example perfect scores (PodX target)
    perfect_scores = {
        'mobility_network': 100,
        'energy_power': 100,
        'reliability': 100,
        'compute_performance': 100,
        'security_compliance': 100,
        'ruggedization': 100,
        'sustainability_tco': 100,
    }
    
    result = calculator.calculate(perfect_scores)
    print(calculator.generate_scorecard(result))


if __name__ == '__main__':
    main()

