import os
import oracledb
from flask import Flask, jsonify, request

app = Flask(__name__)

# Database configuration
dsn = os.getenv('DB_DSN', oracledb.makedsn("192.168.61.225", 1521, service_name="XE"))
db_user = os.getenv('DB_USER', 'system')
db_password = os.getenv('DB_PASSWORD', 'root')

def create_connection():
    try:
        connection = oracledb.connect(user=db_user, password=db_password, dsn=dsn)
        return connection
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        print(f"Error connecting to Oracle DB: {error_obj.message}")
        return None

# Fetch all teams
@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        cursor.execute("SELECT TeamID, TeamName, TotalPoints FROM Teams")

        teams = [{'TeamID': row[0], 'TeamName': row[1], 'TotalPoints': row[2]} for row in cursor.fetchall()]
        cursor.close()
        connection.close()

        return jsonify({"teams": teams})
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        return jsonify({"error": error_obj.message}), 500

# Insert a new player
@app.route('/api/players', methods=['POST'])
def insert_player():
    data = request.get_json()
    player_id = data.get('PlayerID')
    player_name = data.get('PlayerName')
    team_id = data.get('TeamID')

    # if not player_id or not player_name or not team_id:
    #     return jsonify({"error": "PlayerID, PlayerName, and TeamID are required"}), 400

    try:
        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        cursor.execute("INSERT INTO Player (PlayerID, PlayerName, TeamID) VALUES (:1, :2, :3)", 
                       [player_id, player_name, team_id])
        connection.commit()

        return jsonify({"message": f"Player {player_name} added successfully"}), 201
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        return jsonify({"error": error_obj.message}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Fetch all matches
@app.route('/api/matches', methods=['GET'])
def get_matches():
    try:
        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        cursor.execute("SELECT MatchID, Team1ID, Team2ID, Team1Score, Team2Score, MatchDate FROM Match")

        matches = [{'MatchID': row[0], 'Team1ID': row[1], 'Team2ID': row[2], 
                    'Team1Score': row[3], 'Team2Score': row[4], 'MatchDate': row[5]} 
                   for row in cursor.fetchall()]
        cursor.close()
        connection.close()

        return jsonify({"matches": matches})
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        return jsonify({"error": error_obj.message}), 500

# Update match score
@app.route('/api/matches/<int:match_id>/update_score', methods=['PUT'])
def update_match_score(match_id):
    data = request.get_json()
    team1_score = data.get('Team1Score')
    team2_score = data.get('Team2Score')

    if team1_score is None or team2_score is None:
        return jsonify({"error": "Team1Score and Team2Score are required"}), 400

    try:
        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        cursor.execute("UPDATE Match SET Team1Score = :1, Team2Score = :2 WHERE MatchID = :3", 
                       [team1_score, team2_score, match_id])
        connection.commit()

        return jsonify({"message": f"Match {match_id} scores updated successfully"}), 200
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        return jsonify({"error": error_obj.message}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Fetch points table
@app.route('/api/points_table', methods=['GET'])
def get_points_table():
    try:
        connection = create_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor()
        cursor.execute("SELECT TeamID, MatchesPlayed, Wins, Draws, Losses, Points FROM PointsTable")

        points_table = [{'TeamID': row[0], 'MatchesPlayed': row[1], 'Wins': row[2], 
                         'Draws': row[3], 'Losses': row[4], 'Points': row[5]} 
                        for row in cursor.fetchall()]
        cursor.close()
        connection.close()

        return jsonify({"points_table": points_table})
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        return jsonify({"error": error_obj.message}), 500

if __name__ == '__main__':
    app.run(debug=True)
