from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import uuid

from agents.empathy_agent import EmpathyAgent
from agents.visual_agent import VisualAgent
from agents.haggler_agent import HagglerAgent
from agents.finance_agent import FinanceAgent
from agents.orchestrator import AgentOrchestrator, AgentHealthMonitor
from utils.helpers import send_sms, generate_claim_summary

load_dotenv()

# Enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Initialize agents
logger.info("🚀 Initializing AI Agent System...")
empathy_agent = EmpathyAgent()
visual_agent = VisualAgent()
haggler_agent = HagglerAgent()
finance_agent = FinanceAgent()

# Initialize orchestrator (THIS IS THE ADVANCED PART!)
orchestrator = AgentOrchestrator(
    empathy_agent, 
    visual_agent, 
    haggler_agent, 
    finance_agent
)

# Initialize health monitor
health_monitor = AgentHealthMonitor()

logger.info("✓ All systems online")

active_claims = {}

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('../frontend', path)
    except:
        return send_from_directory('../frontend', 'index.html')

# Health check with agent status
@app.route('/api/health', methods=['GET'])
def health_check():
    health_report = health_monitor.get_health_report()
    
    return jsonify({
        'success': True,
        'status': 'healthy',
        'agents': health_report,
        'active_claims': len(active_claims),
        'timestamp': datetime.now().isoformat()
    })

# Enhanced endpoint with orchestrator
@app.route('/api/start-claim', methods=['POST'])
def start_claim():
    """Enhanced claim start with workflow visualization"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        phone_number = data.get('phone', '+61400000000')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        claim_id = str(uuid.uuid4())[:8]
        logger.info(f"📞 Claim #{claim_id}: {user_message[:50]}...")
        
        # Empathy agent with monitoring
        start_time = datetime.now()
        try:
            triage_result = empathy_agent.triage(user_message)
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('empathy', duration, True)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('empathy', duration, False)
            raise
        
        # Create claim with orchestrator state
        active_claims[claim_id] = {
            'id': claim_id,
            'phone': phone_number,
            'initial_message': user_message,
            'triage': triage_result,
            'status': 'triaged',
            'timestamp': datetime.now().isoformat(),
            'steps': ['Empathy Agent: Call received and triaged'],
            'workflow_state': 'triage_complete'
        }
        
        # Get workflow visualization
        workflow_viz = orchestrator.get_workflow_visualization(active_claims[claim_id])
        logger.info(workflow_viz)
        
        base_url = request.host_url.rstrip('/')
        
        return jsonify({
            'success': True,
            'claim_id': claim_id,
            'response': triage_result['response'],
            'triage': triage_result,
            'upload_link': f'{base_url}/upload.html?claim={claim_id}',
            'severity': triage_result['severity'],
            'next_step': 'photo_upload',
            'workflow_state': 'triage_complete',
            'agent_performance': {
                'agent': 'empathy',
                'duration': duration
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Autonomous workflow endpoint (SHOW OFF FEATURE!)
@app.route('/api/autonomous-claim', methods=['POST'])
def autonomous_claim():
    """
    HACKATHON SHOWCASE: Fully autonomous claim processing!
    User just provides message, AI does everything else.
    """
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        phone_number = data.get('phone', '+61400000000')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        claim_id = str(uuid.uuid4())[:8]
        
        logger.info(f"🤖 AUTONOMOUS MODE: Claim #{claim_id}")
        logger.info("=" * 60)
        
        # Prepare claim data
        claim_data = {
            'id': claim_id,
            'message': user_message,
            'phone': phone_number,
            'timestamp': datetime.now().isoformat()
        }
        
        # Execute autonomous workflow via orchestrator
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        workflow_result = loop.run_until_complete(
            orchestrator.execute_autonomous_workflow(claim_data)
        )
        
        if workflow_result['success']:
            # Store completed claim
            active_claims[claim_id] = workflow_result['claim_data']
            active_claims[claim_id]['autonomous'] = True
            
            # Send SMS notification
            contractor = workflow_result['claim_data']['selected_contractor']
            sms_message = (
                f"✅ AUTONOMOUS CLAIM #{claim_id[:6]} COMPLETE!\n\n"
                f"{contractor['name']} dispatched\n"
                f"ETA: {contractor['eta']}\n"
                f"Cost: ${contractor['final_price']}\n\n"
                f"Resolved in {workflow_result['total_time']:.1f} seconds!"
            )
            send_sms(phone_number, sms_message)
            
            logger.info(f"🎉 Autonomous claim completed in {workflow_result['total_time']:.2f}s")
            logger.info(orchestrator.get_workflow_visualization(active_claims[claim_id]))
            logger.info("=" * 60)
            
            return jsonify({
                'success': True,
                'claim_id': claim_id,
                'message': 'Claim processed autonomously!',
                'total_time': workflow_result['total_time'],
                'workflow_log': workflow_result['workflow_log'],
                'contractor': contractor,
                'payment': workflow_result['claim_data']['payment'],
                'summary': generate_claim_summary(active_claims[claim_id])
            })
        else:
            raise Exception(workflow_result.get('error', 'Workflow failed'))
            
    except Exception as e:
        logger.error(f"❌ Autonomous workflow error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Upload damage (same as before but with monitoring)
@app.route('/api/upload-damage', methods=['POST'])
def upload_damage():
    try:
        claim_id = request.form.get('claim_id')
        
        if not claim_id or claim_id not in active_claims:
            return jsonify({'success': False, 'error': 'Invalid claim ID'}), 400
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        logger.info(f"👁️ Visual Agent analyzing for #{claim_id}...")
        
        start_time = datetime.now()
        try:
            assessment = visual_agent.assess_damage(
                image_file, 
                active_claims[claim_id]['triage']
            )
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('visual', duration, True)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('visual', duration, False)
            raise
        
        active_claims[claim_id]['assessment'] = assessment
        active_claims[claim_id]['status'] = 'assessed'
        active_claims[claim_id]['workflow_state'] = 'assessment_complete'
        active_claims[claim_id]['steps'].append('Visual Agent: AI vision analysis complete')
        
        return jsonify({
            'success': True,
            'assessment': assessment,
            'next_step': 'contractor_search',
            'agent_performance': {
                'agent': 'visual',
                'duration': duration
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Find contractor (with monitoring)
@app.route('/api/find-contractor', methods=['POST'])
def find_contractor():
    try:
        data = request.json
        claim_id = data.get('claim_id')
        
        if not claim_id or claim_id not in active_claims:
            return jsonify({'success': False, 'error': 'Invalid claim ID'}), 400
        
        claim = active_claims[claim_id]
        
        logger.info(f"💼 Haggler Agent negotiating for #{claim_id}...")
        
        start_time = datetime.now()
        try:
            negotiation = haggler_agent.negotiate(
                damage_type=claim['triage']['damage_type'],
                severity=claim['triage']['severity'],
                estimated_cost=claim['assessment']['estimated_cost']
            )
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('haggler', duration, True)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('haggler', duration, False)
            raise
        
        active_claims[claim_id]['negotiation'] = negotiation
        active_claims[claim_id]['status'] = 'negotiated'
        active_claims[claim_id]['workflow_state'] = 'negotiation_complete'
        active_claims[claim_id]['steps'].append(
            f'Haggler Agent: {len(negotiation["contractors"])} contractors negotiated'
        )
        
        return jsonify({
            'success': True,
            'negotiation': negotiation,
            'next_step': 'payment',
            'agent_performance': {
                'agent': 'haggler',
                'duration': duration,
                'contractors_contacted': len(negotiation['contractors'])
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Process payment (with monitoring)
@app.route('/api/process-payment', methods=['POST'])
def process_payment():
    try:
        data = request.json
        claim_id = data.get('claim_id')
        contractor_id = data.get('contractor_id', 0)
        
        if not claim_id or claim_id not in active_claims:
            return jsonify({'success': False, 'error': 'Invalid claim ID'}), 400
        
        claim = active_claims[claim_id]
        selected_contractor = claim['negotiation']['contractors'][contractor_id]
        
        logger.info(f"💳 Finance Agent processing for #{claim_id}...")
        
        start_time = datetime.now()
        try:
            payment = finance_agent.process_payment(
                amount=selected_contractor['final_price'],
                contractor=selected_contractor['name']
            )
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('finance', duration, True)
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            health_monitor.record_agent_call('finance', duration, False)
            raise
        
        # Send SMS
        sms_message = (
            f"✅ Claim #{claim_id[:6]} APPROVED!\n\n"
            f"Contractor: {selected_contractor['name']}\n"
            f"Arrival: {selected_contractor['eta']}\n"
            f"Deposit: ${payment['deposit']}\n\n"
            f"Total: ${payment['total_cost']}"
        )
        send_sms(claim['phone'], sms_message)
        
        # Update claim
        active_claims[claim_id]['payment'] = payment
        active_claims[claim_id]['contractor'] = selected_contractor
        active_claims[claim_id]['status'] = 'completed'
        active_claims[claim_id]['workflow_state'] = 'completed'
        active_claims[claim_id]['completion_time'] = datetime.now().isoformat()
        active_claims[claim_id]['steps'].append('Finance Agent: Payment processed, SMS sent')
        
        # Calculate total time
        start = datetime.fromisoformat(claim['timestamp'])
        end = datetime.now()
        total_minutes = (end - start).total_seconds() / 60
        
        logger.info(f"🎉 Claim #{claim_id} completed in {total_minutes:.1f} minutes!")
        logger.info(orchestrator.get_workflow_visualization(active_claims[claim_id]))
        
        return jsonify({
            'success': True,
            'payment': payment,
            'contractor': selected_contractor,
            'completion_time': active_claims[claim_id]['completion_time'],
            'total_time_minutes': round(total_minutes, 1),
            'agent_performance': {
                'agent': 'finance',
                'duration': duration
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Get claim status
@app.route('/api/claim-status/<claim_id>', methods=['GET'])
def claim_status(claim_id):
    if claim_id in active_claims:
        claim = active_claims[claim_id]
        
        # Add workflow visualization
        workflow_viz = orchestrator.get_workflow_visualization(claim)
        
        return jsonify({
            'success': True,
            'claim': claim,
            'workflow_visualization': workflow_viz
        })
    return jsonify({'success': False, 'error': 'Claim not found'}), 404

# Get all claims
@app.route('/api/all-claims', methods=['GET'])
def all_claims():
    return jsonify({
        'success': True,
        'claims': list(active_claims.values()),
        'total': len(active_claims)
    })

# Agent performance dashboard
@app.route('/api/agent-performance', methods=['GET'])
def agent_performance():
    """Get real-time agent performance metrics"""
    health_report = health_monitor.get_health_report()
    dashboard = health_monitor.get_dashboard_ascii()
    
    logger.info(dashboard)
    
    return jsonify({
        'success': True,
        'metrics': health_report,
        'dashboard_ascii': dashboard
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🚨 SOPHIIE RESPONDER - ADVANCED AI SYSTEM 🚨        ║
    ║                                                          ║
    ║           3 Weeks → 3 Minutes → AUTONOMOUS              ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    
    🤖 AI AGENT ORCHESTRA:
       💙 Empathy Agent      - READY (Haiku-powered)
       👁️  Visual Agent       - READY (Sonnet vision)
       💼 Haggler Agent      - READY (Haiku-powered)
       💳 Finance Agent      - READY (Stripe)
       🎭 Orchestrator       - READY (Meta-agent)
       📊 Health Monitor     - READY (Performance tracking)
    
    🌐 ENDPOINTS:
       → http://localhost:{port}
       → http://localhost:{port}/voice.html
       → POST /api/autonomous-claim  🌟 AUTONOMOUS MODE!
       → GET  /api/agent-performance 📊 METRICS DASHBOARD
    
    💡 SPECIAL FEATURES:
       ✓ Multi-agent coordination
       ✓ State machine workflow
       ✓ Performance monitoring
       ✓ Autonomous decision making
       ✓ Smart retry logic
       ✓ Health dashboards
    
    🏆 Sophiie AI Hackathon Ready!
    
    Press Ctrl+C to stop
    ══════════════════════════════════════════════════════════
    """.format(port=port))
    
    app.run(debug=True, port=port, host='0.0.0.0')