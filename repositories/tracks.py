import datetime
from datetime import datetime
from typing import List, Dict, Any
import sqlite3

def select_by_user(conn: sqlite3.Connection, id, user_id) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """WITH liked_tracks AS (
                SELECT TrackID
                FROM Likes
                WHERE UserID = """ + str(user_id) + """
            ),
            owned_tracks AS (
                SELECT TrackID
                FROM TrackOwnership
                WHERE UserID = """ + str(id) + """	
            )
            SELECT 
                Tracks.ID AS TrackID,
                Tracks.AudioFilePath,
                Tracks.TrackCoverPath,
                Tracks.Title,
                Tracks.UploadDate,
                json_group_array(
                    json_object(
                        'UserID', Users.ID,
                        'Username', Users.Username,
                        'Role', TrackOwnershipType.Name
                    )
					ORDER BY TrackOwnershipType.ID
                ) AS Contributors,
                CASE
                    WHEN Tracks.ID IN (SELECT TrackID FROM liked_tracks) THEN 'true'
                    ELSE 'false'
                END AS liked
            FROM TrackOwnership
            JOIN Tracks ON Tracks.ID = TrackOwnership.TrackID 
            JOIN Users ON Users.ID = TrackOwnership.UserID
            JOIN TrackOwnershipType ON TrackOwnershipType.ID = TrackOwnership.OwnershipTypeID
            WHERE Tracks.ID IN (SELECT TrackID FROM owned_tracks)
            GROUP BY Tracks.ID;"""
    ).fetchall()
    return [dict(r) for r in rows]

def select_all_liked(conn: sqlite3.Connection, user_id) -> List[Dict[str, Any]]:
    rows = conn.execute(
        """WITH liked_tracks AS (
                SELECT TrackID
                FROM Likes
                WHERE UserID = """ + str(user_id) + """
            )
            SELECT 
                Tracks.ID AS TrackID,
                Tracks.AudioFilePath,
                Tracks.TrackCoverPath,
                Tracks.Title,
                Tracks.UploadDate,
                json_group_array(
                    json_object(
                        'UserID', Users.ID,
                        'Username', Users.Username,
                        'Role', TrackOwnershipType.Name
                    )
                    ORDER BY TrackOwnershipType.ID
                ) AS Contributors
            FROM TrackOwnership
            JOIN Tracks ON Tracks.ID = TrackOwnership.TrackID 
            JOIN Users ON Users.ID = TrackOwnership.UserID
            JOIN TrackOwnershipType ON TrackOwnershipType.ID = TrackOwnership.OwnershipTypeID
            WHERE Tracks.ID IN (SELECT TrackID FROM liked_tracks)
            GROUP BY Tracks.ID;"""
    ).fetchall()
    return [dict(r) for r in rows]

def add_liked(conn: sqlite3.Connection, track_id, user_id):
    cursor = conn.cursor()
    current_date: datetime = datetime.now();
    print("Track id: " + str(track_id), "User id: " + str(user_id))
    cursor.execute(
        "INSERT INTO Likes (TrackID, UserID, LikeDate) VALUES (?, ?, ?)",
        [track_id, user_id, str(current_date.day) + "-" + str(current_date.month) + "-" + str(current_date.year)],
    )
    conn.commit()

def remove_liked(conn: sqlite3.Connection, track_id, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM Likes WHERE TrackID == ? and UserID == ?",
        [track_id, user_id],
    )
    conn.commit()

def debug_select_all(conn: sqlite3.Connection, current_user_id = 0):
    rows = conn.execute(
        """WITH liked_tracks AS (
                    SELECT TrackID
                    FROM Likes
                    WHERE UserID = """ + str(current_user_id) + """
                )
                SELECT 
                    Tracks.ID AS TrackID,
                    Tracks.AudioFilePath,
                    Tracks.TrackCoverPath,
                    Tracks.Title,
                    Tracks.UploadDate,
                    json_group_array(
                        json_object(
                            'UserID', Users.ID,
                            'Username', Users.Username,
                            'Role', TrackOwnershipType.Name
                        )
    					ORDER BY TrackOwnershipType.ID
                    ) AS Contributors,
                    CASE
                        WHEN Tracks.ID IN (SELECT TrackID FROM liked_tracks) THEN 'true'
                        ELSE 'false'
                    END AS liked
                FROM TrackOwnership
                JOIN Tracks ON Tracks.ID = TrackOwnership.TrackID 
                JOIN Users ON Users.ID = TrackOwnership.UserID
                JOIN TrackOwnershipType ON TrackOwnershipType.ID = TrackOwnership.OwnershipTypeID
                GROUP BY Tracks.ID;"""
    ).fetchall()
    return [dict(r) for r in rows]

def select_by_text(conn: sqlite3.Connection, query, current_user_id = 0):
    rows = conn.execute(
        """WITH liked_tracks AS (
            SELECT TrackID
            FROM Likes
            WHERE UserID = """ + str(current_user_id) + """
        )
        SELECT 
            Tracks.ID AS TrackID,
            Tracks.AudioFilePath,
            Tracks.TrackCoverPath,
            Tracks.Title,
            Tracks.UploadDate,
            json_group_array(
                json_object(
                    'UserID', Users.ID,
                    'Username', Users.Username,
                    'Role', TrackOwnershipType.Name
                )
                ORDER BY TrackOwnershipType.ID
            ) AS Contributors,
            CASE
                WHEN Tracks.ID IN (SELECT TrackID FROM liked_tracks) THEN 'true'
                ELSE 'false'
            END AS liked
        FROM TrackOwnership
        JOIN Tracks ON Tracks.ID = TrackOwnership.TrackID 
        JOIN Users ON Users.ID = TrackOwnership.UserID
        JOIN TrackOwnershipType ON TrackOwnershipType.ID = TrackOwnership.OwnershipTypeID
        WHERE Tracks.Title LIKE '%""" + str(query) + """%' OR Users.Username LIKE '%""" + str(query) + """%'
        GROUP BY Tracks.ID;"""
    ).fetchall()
    return [dict(r) for r in rows]

def insert(conn: sqlite3.Connection, title: str, audio_file_path: str, track_cover_path: str, current_user_id: str):
    now = datetime.now()
    upload_date = f"{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}"

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tracks(Title, AudioFilePath, TrackCoverPath, UploadDate) VALUES (?, ?, ?, ?)",
        (title, audio_file_path, track_cover_path, upload_date)
    )
    conn.commit()
    track_id = cursor.lastrowid
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO TrackOwnership(UserID, TrackID, OwnershipTypeID) VALUES (?, ?, 1)",
        (current_user_id, track_id)
    )
    conn.commit()
