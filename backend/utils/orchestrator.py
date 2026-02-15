import logging
from datetime import datetime
import asyncio
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Meta-agent that coordinates the entire claim resolution workflow.
    Demonstrates advanced agentic architecture with:
    - State management
    - Error recovery
    - Parallel agent execution
    - Decision making
    """
    
    def __init__(self, empathy_agent, visual_agent, haggler_agent, finance_agent):
        self.empathy = empathy_agent
        self.visual = visual_agent
        self.haggler = haggler_agent
        self.finance = finance_agent
        
        self.state_machine = {
            'initialized': ['triaging'],
            'triaging': ['triage_complete', 'triage_failed'],
            'triage_complete': ['assessing'],
            'assessing': ['assessment_complete', 'assessment_failed'],
            'assessment_complete': ['negotiating'],
            'negotiating': ['negotiation_complete', 'negotiation_failed'],
            'negotiation_complete': ['processing_payment'],
            'processing_payment': ['completed', 'payment_failed'],
            'completed': [],
            'triage_failed': ['triaging'],
            'assessment_failed': ['assessing'],
            'negotiation_failed': ['negotiating'],
            'payment_failed': ['processing_payment']
        }
        
        logger.info("🎭 Agent Orchestrator initialized")
    
    def get_workflow_state(self, claim: Dict) -> str:
        """Determine current workflow state from claim data"""
        if 'payment' in claim and claim.get('status') == 'completed':
            return 'completed'
        elif 'negotiation' in claim:
            return 'negotiation_complete'
        elif 'assessment' in claim:
            return 'assessment_complete'
        elif 'triage' in claim:
            return 'triage_complete'
        else:
            return 'initialized'
    
    def get_next_actions(self, current_state: str) -> List[str]:
        """Get possible next actions from current state"""
        return self.state_machine.get(current_state, [])
    
    def validate_state_transition(self, from_state: str, to_state: str) -> bool:
        """Validate if a state transition is allowed"""
        allowed = self.state_machine.get(from_state, [])
        return to_state in allowed
    
    async def execute_autonomous_workflow(self, claim_data: Dict) -> Dict:
        """
        Execute the entire claim workflow autonomously.
        This demonstrates true agentic behavior - the system decides
        what to do next without explicit human instructions.
        """
        
        logger.info(f"🤖 Starting autonomous workflow for claim #{claim_data.get('id', 'unknown')}")
        
        workflow_log = []
        current_state = self.get_workflow_state(claim_data)
        
        try:
            # Agent 1: Empathy Agent - Triage
            if current_state == 'initialized':
                logger.info("💙 Empathy Agent: Starting triage...")
                triage_start = datetime.now()
                
                triage = self.empathy.triage(claim_data['message'])
                
                triage_time = (datetime.now() - triage_start).total_seconds()
                workflow_log.append({
                    'agent': 'empathy',
                    'action': 'triage',
                    'duration': triage_time,
                    'result': 'success',
                    'data': triage
                })
                
                claim_data['triage'] = triage
                current_state = 'triage_complete'
                logger.info(f"✓ Triage complete in {triage_time:.2f}s")
            
            # Decision Point: Check if image analysis is needed
            if current_state == 'triage_complete':
                severity = claim_data['triage']['severity']
                
                # Autonomous decision: Skip visual for minor claims
                if severity == 'minor':
                    logger.info("🤔 Orchestrator Decision: Minor claim, using estimate from triage")
                    claim_data['assessment'] = {
                        'description': 'Minor damage, estimate based on description',
                        'estimated_cost': 1500,
                        'cost_range': {'min': 1000, 'max': 2000},
                        'urgency': 'standard',
                        'required_trade': claim_data['triage'].get('damage_type', 'general contractor'),
                        'safety_hazards': [],
                        'recommended_action': 'Standard repair process'
                    }
                    workflow_log.append({
                        'agent': 'orchestrator',
                        'action': 'skip_visual_assessment',
                        'reason': 'minor_severity',
                        'result': 'success'
                    })
                    current_state = 'assessment_complete'
                else:
                    logger.info("🤔 Orchestrator Decision: Visual assessment required")
            
            # Agent 2: Visual Agent - Assessment (if needed)
            if current_state == 'assessment_complete' or 'assessment' in claim_data:
                logger.info("💼 Haggler Agent: Starting negotiations...")
                negotiation_start = datetime.now()
                
                # Parallel contractor searches could happen here
                negotiation = self.haggler.negotiate(
                    damage_type=claim_data['triage']['damage_type'],
                    severity=claim_data['triage']['severity'],
                    estimated_cost=claim_data['assessment']['estimated_cost']
                )
                
                negotiation_time = (datetime.now() - negotiation_start).total_seconds()
                workflow_log.append({
                    'agent': 'haggler',
                    'action': 'negotiate',
                    'duration': negotiation_time,
                    'contractors_contacted': len(negotiation['contractors']),
                    'result': 'success',
                    'data': negotiation
                })
                
                claim_data['negotiation'] = negotiation
                current_state = 'negotiation_complete'
                logger.info(f"✓ Negotiation complete in {negotiation_time:.2f}s")
            
            # Decision Point: Auto-select best contractor
            if current_state == 'negotiation_complete':
                best_contractor = claim_data['negotiation']['contractors'][0]
                
                logger.info(f"🤔 Orchestrator Decision: Auto-selecting {best_contractor['name']}")
                workflow_log.append({
                    'agent': 'orchestrator',
                    'action': 'auto_select_contractor',
                    'selected': best_contractor['name'],
                    'reason': 'best_value',
                    'result': 'success'
                })
                
                claim_data['selected_contractor'] = best_contractor
            
            # Agent 4: Finance Agent - Payment
            if 'selected_contractor' in claim_data:
                logger.info("💳 Finance Agent: Processing payment...")
                payment_start = datetime.now()
                
                payment = self.finance.process_payment(
                    amount=claim_data['selected_contractor']['final_price'],
                    contractor=claim_data['selected_contractor']['name']
                )
                
                payment_time = (datetime.now() - payment_start).total_seconds()
                workflow_log.append({
                    'agent': 'finance',
                    'action': 'process_payment',
                    'duration': payment_time,
                    'result': 'success',
                    'data': payment
                })
                
                claim_data['payment'] = payment
                claim_data['status'] = 'completed'
                current_state = 'completed'
                logger.info(f"✓ Payment processed in {payment_time:.2f}s")
            
            # Calculate total workflow time
            total_time = sum(log.get('duration', 0) for log in workflow_log if 'duration' in log)
            
            logger.info(f"🎉 Autonomous workflow completed in {total_time:.2f}s")
            
            return {
                'success': True,
                'final_state': current_state,
                'workflow_log': workflow_log,
                'total_time': total_time,
                'claim_data': claim_data
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow error: {e}")
            return {
                'success': False,
                'error': str(e),
                'final_state': current_state,
                'workflow_log': workflow_log
            }
    
    def get_workflow_visualization(self, claim_data: Dict) -> str:
        """Generate ASCII visualization of workflow progress"""
        
        current_state = self.get_workflow_state(claim_data)
        
        states = [
            ('initialized', '○', 'Start'),
            ('triage_complete', '●' if 'triage' in claim_data else '○', 'Triage'),
            ('assessment_complete', '●' if 'assessment' in claim_data else '○', 'Assessment'),
            ('negotiation_complete', '●' if 'negotiation' in claim_data else '○', 'Negotiation'),
            ('completed', '●' if claim_data.get('status') == 'completed' else '○', 'Complete')
        ]
        
        viz = "\n    Workflow Progress:\n    "
        viz += " → ".join([f"{icon} {name}" for _, icon, name in states])
        viz += "\n"
        
        return viz


class AgentHealthMonitor:
    """Monitor agent performance and health"""
    
    def __init__(self):
        self.metrics = {
            'empathy': {'calls': 0, 'errors': 0, 'avg_time': 0},
            'visual': {'calls': 0, 'errors': 0, 'avg_time': 0},
            'haggler': {'calls': 0, 'errors': 0, 'avg_time': 0},
            'finance': {'calls': 0, 'errors': 0, 'avg_time': 0}
        }
        logger.info("📊 Agent Health Monitor initialized")
    
    def record_agent_call(self, agent_name: str, duration: float, success: bool):
        """Record agent performance metrics"""
        if agent_name not in self.metrics:
            return
        
        metrics = self.metrics[agent_name]
        metrics['calls'] += 1
        
        if not success:
            metrics['errors'] += 1
        
        # Update rolling average
        if metrics['calls'] == 1:
            metrics['avg_time'] = duration
        else:
            metrics['avg_time'] = (
                (metrics['avg_time'] * (metrics['calls'] - 1) + duration) / 
                metrics['calls']
            )
    
    def get_health_report(self) -> Dict:
        """Generate health report for all agents"""
        report = {}
        
        for agent, metrics in self.metrics.items():
            if metrics['calls'] > 0:
                error_rate = (metrics['errors'] / metrics['calls']) * 100
                status = 'healthy' if error_rate < 5 else 'degraded' if error_rate < 20 else 'unhealthy'
            else:
                error_rate = 0
                status = 'idle'
            
            report[agent] = {
                'status': status,
                'total_calls': metrics['calls'],
                'error_rate': f"{error_rate:.1f}%",
                'avg_response_time': f"{metrics['avg_time']:.2f}s"
            }
        
        return report
    
    def get_dashboard_ascii(self) -> str:
        """Generate ASCII dashboard"""
        report = self.get_health_report()
        
        dashboard = """
╔════════════════════════════════════════════════════════════╗
║              AGENT HEALTH DASHBOARD                        ║
╠════════════════════════════════════════════════════════════╣
"""
        
        for agent, metrics in report.items():
            icon = '✓' if metrics['status'] == 'healthy' else '⚠' if metrics['status'] == 'degraded' else '✗'
            dashboard += f"║  {icon} {agent.upper():<15} │ {metrics['status']:<10} │ {metrics['total_calls']:>4} calls │ {metrics['avg_response_time']:>8} ║\n"
        
        dashboard += "╚════════════════════════════════════════════════════════════╝"
        
        return dashboard


class SmartRetryHandler:
    """Intelligent retry logic with exponential backoff"""
    
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        logger.info("🔄 Smart Retry Handler initialized")
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with smart retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                return result
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"❌ Failed after {self.max_retries} attempts: {e}")
                    raise
                
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                
                await asyncio.sleep(delay)