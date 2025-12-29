"""
WebSocket event handlers for real-time updates
"""
from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio
import logging

logger = logging.getLogger(__name__)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected', 'message': 'Connected to ABKBet live updates'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')


@socketio.on('subscribe_match')
def handle_subscribe_match(data):
    """Subscribe to updates for a specific match"""
    match_id = data.get('match_id')
    if match_id:
        room = f'match_{match_id}'
        join_room(room)
        logger.info(f'Client {request.sid} subscribed to match {match_id}')
        emit('subscribed', {'match_id': match_id, 'room': room})


@socketio.on('unsubscribe_match')
def handle_unsubscribe_match(data):
    """Unsubscribe from match updates"""
    match_id = data.get('match_id')
    if match_id:
        room = f'match_{match_id}'
        leave_room(room)
        logger.info(f'Client {request.sid} unsubscribed from match {match_id}')
        emit('unsubscribed', {'match_id': match_id})


@socketio.on('subscribe_live_matches')
def handle_subscribe_live_matches():
    """Subscribe to all live match updates"""
    join_room('live_matches')
    logger.info(f'Client {request.sid} subscribed to live matches')
    emit('subscribed', {'room': 'live_matches'})


@socketio.on('unsubscribe_live_matches')
def handle_unsubscribe_live_matches():
    """Unsubscribe from live match updates"""
    leave_room('live_matches')
    logger.info(f'Client {request.sid} unsubscribed from live matches')
    emit('unsubscribed', {'room': 'live_matches'})


def broadcast_match_update(match_data):
    """
    Broadcast match update to subscribed clients
    Called from Celery tasks when match data changes
    
    Args:
        match_data: Dictionary containing match information
    """
    match_id = match_data.get('id')
    room = f'match_{match_id}'
    
    socketio.emit('match_update', match_data, room=room)
    socketio.emit('match_update', match_data, room='live_matches')
    logger.debug(f'Broadcast match update for match {match_id}')


def broadcast_odds_update(match_id, odds_data):
    """
    Broadcast odds update to subscribed clients
    
    Args:
        match_id: Match ID
        odds_data: Dictionary containing updated odds
    """
    room = f'match_{match_id}'
    
    socketio.emit('odds_update', {
        'match_id': match_id,
        'odds': odds_data
    }, room=room)
    logger.debug(f'Broadcast odds update for match {match_id}')


def broadcast_bet_settled(bet_data):
    """
    Broadcast bet settlement notification to user
    
    Args:
        bet_data: Dictionary containing bet information
    """
    user_id = bet_data.get('user_id')
    room = f'user_{user_id}'
    
    socketio.emit('bet_settled', bet_data, room=room)
    logger.info(f'Broadcast bet settlement to user {user_id}')
