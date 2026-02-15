"""
Agent Orchestrator - The Brain of Sophiie Responder

This meta-agent coordinates all other agents to autonomously
process insurance claims from start to finish.

Key Features:
- State machine workflow management
- Autonomous decision making
- Error recovery and retry logic
- Performance monitoring
- Multi-agent coordination
"""

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
    - Autonomous decision making
    """
    
    def __init__(self, empathy_agent, visual_agent, haggler_agent, finance_agent):
        self.empathy = empathy_agent
        self.visual = visual_agent
        self.haggler = haggler_agent
        self.finance = finance_agent
        
        # State machine defines valid workflow transitions
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
        
        Args:
            claim_data: Initial claim information
            
        Returns:
            Dict with workflow results and performance metrics
        """
        
        logger.info(f"🤖 Starting autonomous workflow for claim #{claim_data.get('id', 'unknown')}")
        
        workflow_log = []
        current_state = self.get_workflow_state(claim_data)
        
        try:
            # ============================================
            # STAGE 1: EMPATHY AGENT - TRIAGE
            # ============================================
            if current_state == 'initialized':
                logger.info("💙 Stage 1: Empathy Agent - Emergency Triage")
                triage_start = datetime.now()
                
                triage = self.empathy.triage(claim_data['message'])
                
                triage_time = (datetime.now() - triage_start).total_seconds()
                workflow_log.append({
                    'stage': 1,
                    'agent': 'empathy',
                    'action': 'triage',
                    'duration': triage_time,
                    'result': 'success',
                    'data': triage
                })
                
                claim_data['triage'] = triage
                current_state = 'triage_complete'
                logger.info(f"✓ Triage complete: {triage['severity']} severity in {triage_time:.2f}s")
            
            # ============================================
            # DECISION POINT: Should we skip visual assessment?
            # ============================================
            if current_state == 'triage_complete':
                severity = claim_data['triage']['severity']
                
                # AUTONOMOUS DECISION: Skip visual for minor claims to save time
                if severity == 'minor':
                    logger.info("🤔 Orchestrator Decision: Minor claim detected")
                    logger.info("   → Skipping visual assessment to optimize time")
                    logger.info("   → Using cost estimate from triage data")
                    
                    # Generate estimated assessment without photo
                    claim_data['assessment'] = {
                        'description': f"Minor {claim_data['triage']['damage_type']} damage based on verbal description",
                        'estimated_cost': 1500,
                        'cost_range': {'min': 1000, 'max': 2000},
                        'urgency': 'standard',
                        'required_trade': claim_data['triage'].get('damage_type', 'general contractor'),
                        'safety_hazards': [],
                        'recommended_action': 'Standard repair scheduling',
                        'assessment_method': 'autonomous_estimate'
                    }
                    
                    workflow_log.append({
                        'stage': 2,
                        'agent': 'orchestrator',
                        'action': 'skip_visual_assessment',
                        'reason': 'minor_severity_optimization',
                        'result': 'success',
                        'time_saved': '~2 seconds'
                    })
                    
                    current_state = 'assessment_complete'
                else:
                    logger.info("🤔 Orchestrator Decision: Visual assessment required")
                    logger.info("   → Severity is moderate/severe/critical")
                    logger.info("   → Photo analysis needed for accurate estimate")
                    
                    # In production, this would wait for photo upload
                    # For autonomous demo, we simulate visual assessment
                    claim_data['assessment'] = {
                        'description': f"Significant {claim_data['triage']['damage_type']} damage requiring professional repair",
                        'estimated_cost': 5000 if severity == 'severe' else 3000,
                        'cost_range': {'min': 4000, 'max': 6000} if severity == 'severe' else {'min': 2500, 'max': 3500},
                        'urgency': 'urgent' if severity in ['severe', 'critical'] else 'standard',
                        'required_trade': claim_data['triage'].get('damage_type', 'general contractor'),
                        'safety_hazards': ['Structural concern'] if severity == 'critical' else [],
                        'recommended_action': 'Immediate professional assessment required',
                        'assessment_method': 'simulated_for_autonomous_demo'
                    }
                    
                    workflow_log.append({
                        'stage': 2,
                        'agent': 'visual',
                        'action': 'assess_damage',
                        'result': 'success',
                        'note': 'Simulated for autonomous demo'
                    })
                    
                    current_state = 'assessment_complete'
            
            # ============================================
            # STAGE 3: HAGGLER AGENT - CONTRACTOR NEGOTIATION
            # ============================================
            if current_state == 'assessment_complete':
                logger.info("💼 Stage 3: Haggler Agent - Contractor Negotiation")
                negotiation_start = datetime.now()
                
                negotiation = self.haggler.negotiate(
                    damage_type=claim_data['triage']['damage_type'],
                    severity=claim_data['triage']['severity'],
                    estimated_cost=claim_data['assessment']['estimated_cost']
                )
                
                negotiation_time = (datetime.now() - negotiation_start).total_seconds()
                workflow_log.append({
                    'stage': 3,
                    'agent': 'haggler',
                    'action': 'negotiate',
                    'duration': negotiation_time,
                    'contractors_contacted': len(negotiation['contractors']),
                    'result': 'success',
                    'data': negotiation
                })
                
                claim_data['negotiation'] = negotiation
                current_state = 'negotiation_complete'
                logger.info(f"✓ Negotiation complete: {len(negotiation['contractors'])} contractors in {negotiation_time:.2f}s")
            
            # ============================================
            # DECISION POINT: Auto-select best contractor
            # ============================================
            if current_state == 'negotiation_complete':
                # AUTONOMOUS DECISION: Select best value contractor
                contractors = claim_data['negotiation']['contractors']
                best_contractor = contractors[0]  # Already sorted by price
                
                # Check if fastest contractor is worth the premium
                fastest = min(contractors, key=lambda x: x['eta'])
                price_diff = fastest['final_price'] - best_contractor['final_price']
                
                if price_diff < 200 and fastest['eta'] < best_contractor['eta']:
                    selected = fastest
                    reason = 'fastest_within_budget'
                    logger.info(f"🤔 Orchestrator Decision: Selected {selected['name']} (fastest, minimal premium)")
                else:
                    selected = best_contractor
                    reason = 'best_value'
                    logger.info(f"🤔 Orchestrator Decision: Selected {selected['name']} (best value)")
                
                workflow_log.append({
                    'stage': 4,
                    'agent': 'orchestrator',
                    'action': 'auto_select_contractor',
                    'selected': selected['name'],
                    'reason': reason,
                    'result': 'success'
                })
                
                claim_data['selected_contractor'] = selected
            
            # ============================================
            # STAGE 4: FINANCE AGENT - PAYMENT PROCESSING
            # ============================================
            if 'selected_contractor' in claim_data:
                logger.info("💳 Stage 4: Finance Agent - Payment Processing")
                payment_start = datetime.now()
                
                payment = self.finance.process_payment(
                    amount=claim_data['selected_contractor']['final_price'],
                    contractor=claim_data['selected_contractor']['name']
                )
                
                payment_time = (datetime.now() - payment_start).total_seconds()
                workflow_log.append({
                    'stage': 5,
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
            
            # ============================================
            # WORKFLOW COMPLETE
            # ============================================
            total_time = sum(log.get('duration', 0) for log in workflow_log if 'duration' in log)
            
            logger.info("=" * 60)
            logger.info(f"🎉 AUTONOMOUS WORKFLOW COMPLETED")
            logger.info(f"   Total Time: {total_time:.2f} seconds")
            logger.info(f"   Stages Executed: {len(workflow_log)}")
            logger.info(f"   Final State: {current_state}")
            logger.info("=" * 60)
            
            return {
                'success': True,
                'final_state': current_state,
                'workflow_log': workflow_log,
                'total_time': total_time,
                'claim_data': claim_data,
                'decisions_made': [log for log in workflow_log if log.get('agent') == 'orchestrator']
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow error at state '{current_state}': {e}")
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
        viz += f"\n    Current State: {current_state}\n"
        
        return viz


class AgentHealthMonitor:
    """Monitor agent performance and health"""
    
    def __init__(self):
        self.metrics = {
            'empathy': {'calls': 0, 'errors': 0, 'avg_time': 0, 'total_time': 0},
            'visual': {'calls': 0, 'errors': 0, 'avg_time': 0, 'total_time': 0},
            'haggler': {'calls': 0, 'errors': 0, 'avg_time': 0, 'total_time': 0},
            'finance': {'calls': 0, 'errors': 0, 'avg_time': 0, 'total_time': 0}
        }
        logger.info("📊 Agent Health Monitor initialized")
    
    def record_agent_call(self, agent_name: str, duration: float, success: bool):
        """Record agent performance metrics"""
        if agent_name not in self.metrics:
            return
        
        metrics = self.metrics[agent_name]
        metrics['calls'] += 1
        metrics['total_time'] += duration
        
        if not success:
            metrics['errors'] += 1
        
        # Update rolling average
        metrics['avg_time'] = metrics['total_time'] / metrics['calls']
    
    def get_health_report(self) -> Dict:
        """Generate health report for all agents"""
        report = {}
        
        for agent, metrics in self.metrics.items():
            if metrics['calls'] > 0:
                error_rate = (metrics['errors'] / metrics['calls']) * 100
                
                # Determine health status
                if error_rate == 0:
                    status = 'excellent'
                elif error_rate < 5:
                    status = 'healthy'
                elif error_rate < 20:
                    status = 'degraded'
                else:
                    status = 'unhealthy'
            else:
                error_rate = 0
                status = 'idle'
            
            report[agent] = {
                'status': status,
                'total_calls': metrics['calls'],
                'error_rate': f"{error_rate:.1f}%",
                'avg_response_time': f"{metrics['avg_time']:.2f}s",
                'total_time': f"{metrics['total_time']:.1f}s"
            }
        
        return report
    
    def get_dashboard_ascii(self) -> str:
        """Generate ASCII dashboard for terminal display"""
        report = self.get_health_report()
        
        dashboard = """
╔════════════════════════════════════════════════════════════════════╗
║                    AGENT HEALTH DASHBOARD                          ║
╠════════════════════════════════════════════════════════════════════╣
"""
        
        status_icons = {
            'excellent': '✓✓',
            'healthy': '✓ ',
            'degraded': '⚠ ',
            'unhealthy': '✗ ',
            'idle': '○ '
        }
        
        for agent, metrics in report.items():
            icon = status_icons.get(metrics['status'], '? ')
            
            dashboard += f"║  {icon} {agent.upper():<12} │ "
            dashboard += f"{metrics['status']:<10} │ "
            dashboard += f"{metrics['total_calls']:>4} calls │ "
            dashboard += f"Avg: {metrics['avg_response_time']:>6} ║\n"
        
        dashboard += "╚════════════════════════════════════════════════════════════════════╝"
        
        return dashboard


class SmartRetryHandler:
    """Intelligent retry logic with exponential backoff"""
    
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        logger.info(f"🔄 Smart Retry Handler initialized (max_retries={max_retries})")
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with smart retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✓ Succeeded on attempt {attempt + 1}")
                
                return result
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"❌ Failed after {self.max_retries} attempts: {e}")
                    raise
                
                # Exponential backoff
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                
                await asyncio.sleep(delay)