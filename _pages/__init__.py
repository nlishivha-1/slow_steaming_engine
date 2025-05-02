from .vessel_input import app as vessel_input
from .speed_optimization import app as speed_optimization
from .route_optimization import app as route_optimization
from .cost_benefit import app as cost_benefit
from .emissions import app as emissions
from .dashboard import app as dashboard

__all__ = [
    'vessel_input',
    'speed_optimization',
    'route_optimization',
    'cost_benefit',
    'emissions',
    'dashboard'
]
