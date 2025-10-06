#!/usr/bin/env python3
"""
Advanced YouTube Video Scoring System
Provides comprehensive scoring for music video selection based on multiple factors
Uses mathematical precision and logarithmic scaling for accurate differentiation
"""

import re
import math
from datetime import datetime
from difflib import SequenceMatcher


class YouTubeScorer:
    """Advanced scoring system for YouTube video selection with ultra-precise algorithms"""
    
    def __init__(self):
        # Scoring weights configuration (fine-tuned for optimal balance)
        # Title matching is now the DOMINANT factor - accuracy over popularity
        self.weights = {
            'title_exact_match': 300,      # MASSIVELY increased - title accuracy is king
            'title_similarity': 200,        # MASSIVELY increased - fuzzy matching very important
            'title_mismatch_penalty': 250,  # NEW: Heavy penalty for missing key words
            'artist_match': 80,             # Increased artist importance
            'official_content': 30,         # Reduced weight for official content
            'verified_artist': 40,          # Reduced - not as important as title match
            'views': 50,                    # HALVED - popularity is secondary
            'likes': 40,                    # HALVED - popularity is secondary
            'like_ratio': 30,               # Reduced
            'comment_count': 15,            # Reduced
            'duration': 30,                 # Music track appropriateness
            'recency': 20,                  # Reduced
            'audio_quality': 25,            # Quality indicators
            'upload_frequency': 10,         # Reduced
            'subscriber_count': 20,         # Reduced - channel authority less important
            'view_velocity': 15,            # Reduced
            'engagement_score': 25,         # Reduced
        }
        
        # Minimum title similarity threshold (0-1 scale)
        # Videos below this threshold will get massive penalties
        self.min_title_similarity = 0.35  # Require at least 35% title match
        
        # Mathematical constants for logarithmic scaling
        self.log_base_views = 1.5       # Base for view count logarithm
        self.log_base_likes = 1.6       # Base for like count logarithm
        self.log_base_comments = 1.7    # Base for comment count logarithm
        
        # Official/verified indicators
        self.official_keywords = [
            'official', 'vevo', 'records', 'music', 'audio', 
            'video', 'mv', 'official music video', 'official audio'
        ]
        
        self.verified_channels = [
            'vevo', 'records', 'official', 'music', 'entertainment',
            'label', 'studios', 'productions'
        ]
        
        # Non-music content penalties
        self.penalty_keywords = [
            'reaction', 'reacting', 'review', 'reviewed',
            'interview', 'documentary', 'behind the scenes', 'bts',
            'making of', 'how to', 'tutorial', 'lesson',
            'cover', 'covered by', 'amateur', 'practice',
            'karaoke', 'instrumental', 'backing track',
            'gameplay', 'gaming', 'let\'s play',
            'vlog', 'podcast', 'talk show',
            'parody', 'spoof', 'funny', 'meme',
            'remix', 'nightcore', 'slowed', 'reverb',
            'fan made', 'unofficial', 'bootleg'
        ]
        
        # Quality indicators
        self.quality_indicators = [
            '4k', 'hd', 'high quality', 'hq', 'remastered',
            'official music video', 'official audio', 'explicit',
            'clean version', 'radio edit', 'album version'
        ]
        
    def score_video(self, video_info, query, verbose=False):
        """
        Comprehensive scoring of a YouTube video for music search
        
        Args:
            video_info: Dictionary containing video metadata
            query: Original search query (format: "Title - Artist")
            verbose: If True, print detailed scoring breakdown
            
        Returns:
            Total score and scoring breakdown dictionary
        """
        breakdown = {}
        total_score = 0
        
        # Extract video information
        title = (video_info.get('title', '') or '').lower()
        uploader = (video_info.get('uploader', '') or '').lower()
        channel_id = video_info.get('channel_id', '')
        duration = video_info.get('duration', 0) or 0
        view_count = video_info.get('view_count') or 0
        like_count = video_info.get('like_count') or 0
        comment_count = video_info.get('comment_count') or 0
        upload_date = video_info.get('upload_date', '')
        description = (video_info.get('description', '') or '').lower()
        subscriber_count = video_info.get('channel_follower_count') or 0
        
        # Parse query into song and artist
        song_title, artist_name = self._parse_query(query)
        
        # 1. TITLE MATCHING SCORE
        title_score = self._score_title_match(title, song_title, artist_name)
        breakdown['title_match'] = title_score
        total_score += title_score
        
        # 2. ARTIST MATCHING SCORE
        artist_score = self._score_artist_match(title, uploader, description, artist_name)
        breakdown['artist_match'] = artist_score
        total_score += artist_score
        
        # 3. OFFICIAL CONTENT SCORE
        official_score = self._score_official_content(title, uploader, description, channel_id)
        breakdown['official_content'] = official_score
        total_score += official_score
        
        # 4. POPULARITY SCORE (Views + Likes + Engagement)
        popularity_score = self._score_popularity(view_count, like_count, comment_count)
        breakdown['popularity'] = popularity_score
        total_score += popularity_score
        
        # 5. ENGAGEMENT QUALITY SCORE (Like ratio)
        engagement_score = self._score_engagement_quality(view_count, like_count, comment_count)
        breakdown['engagement_quality'] = engagement_score
        total_score += engagement_score
        
        # 6. DURATION SCORE
        duration_score = self._score_duration(duration)
        breakdown['duration'] = duration_score
        total_score += duration_score
        
        # 7. RECENCY SCORE
        recency_score = self._score_recency(upload_date)
        breakdown['recency'] = recency_score
        total_score += recency_score
        
        # 8. QUALITY INDICATORS SCORE
        quality_score = self._score_quality_indicators(title, description)
        breakdown['quality_indicators'] = quality_score
        total_score += quality_score
        
        # 9. CHANNEL AUTHORITY SCORE
        channel_score = self._score_channel_authority(uploader, subscriber_count, channel_id)
        breakdown['channel_authority'] = channel_score
        total_score += channel_score
        
        # 10. CONTENT TYPE PENALTIES
        penalty_score = self._score_penalties(title, description)
        breakdown['penalties'] = penalty_score
        total_score += penalty_score  # This will be negative
        
        # 11. DESCRIPTION RELEVANCE SCORE
        description_score = self._score_description(description, song_title, artist_name)
        breakdown['description'] = description_score
        total_score += description_score
        
        # 12. VIEW VELOCITY SCORE (Trending factor)
        velocity_score = self._calculate_view_velocity_score(view_count, upload_date, self.weights['view_velocity'])
        breakdown['view_velocity'] = velocity_score
        total_score += velocity_score
        
        # 13. QUALITY CONFIDENCE MULTIPLIER (Authenticity check)
        quality_confidence = self._calculate_quality_confidence_score(view_count, like_count, subscriber_count)
        breakdown['quality_confidence'] = quality_confidence
        
        # Apply quality confidence multiplier to the total score
        total_score *= quality_confidence
        
        # 14. COMBINED ENGAGEMENT SCORE (Holistic engagement metric)
        if view_count > 0:
            combined_engagement = (
                (like_count / view_count * 100) * 0.6 +  # Like ratio weight
                (comment_count / view_count * 100) * 0.3 +  # Comment ratio weight
                (min(subscriber_count / 100000, 10)) * 0.1  # Channel authority weight
            )
            engagement_bonus = min(combined_engagement * self.weights['engagement_score'] / 10, self.weights['engagement_score'])
            breakdown['combined_engagement'] = engagement_bonus
            total_score += engagement_bonus
        
        # Ensure score doesn't go negative
        total_score = max(0, total_score)
        
        if verbose:
            self._print_breakdown(breakdown, total_score, video_info)
        
        return total_score, breakdown
    
    def _parse_query(self, query):
        """Parse query into song title and artist name"""
        if ' - ' in query:
            parts = query.split(' - ', 1)
            return parts[0].strip().lower(), parts[1].strip().lower()
        return query.lower(), ''
    
    def _score_title_match(self, title, song_title, artist_name):
        """Score based on title matching with advanced algorithms - TITLE ACCURACY IS PARAMOUNT"""
        score = 0
        penalty = 0
        
        # Extract significant words from song title (>2 chars, not common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        song_words = [w for w in song_title.split() if len(w) > 2 and w not in common_words]
        title_lower = title.lower()
        title_words = title.split()
        
        # Count how many key words from song title are in video title
        matched_key_words = sum(1 for word in song_words if word in title_lower)
        
        # ==========================================
        # CRITICAL: TITLE MISMATCH PENALTY
        # ==========================================
        # If key words are missing, apply HEAVY penalty
        if song_words:
            missing_word_ratio = 1 - (matched_key_words / len(song_words))
            if missing_word_ratio > 0:
                # Apply exponential penalty for missing words
                penalty -= (missing_word_ratio ** 2) * self.weights['title_mismatch_penalty']
                
                # Extra harsh penalty if more than 50% of key words are missing
                if missing_word_ratio > 0.5:
                    penalty -= 200  # Massive penalty
                    
                # If completely wrong title (no key words match), essentially disqualify it
                if matched_key_words == 0 and len(song_words) > 0:
                    penalty -= 500  # Almost impossible to overcome
        
        # 1. EXACT PHRASE MATCH (Highest priority)
        if song_title in title:
            score += self.weights['title_exact_match']
            
            # Bonus if it's at the start of the title (stronger signal)
            if title.startswith(song_title):
                score += 100  # Huge bonus
        else:
            # Penalty for NOT having exact phrase match
            penalty -= 50
        
        # 2. FUZZY STRING SIMILARITY (Levenshtein-based)
        similarity = SequenceMatcher(None, song_title, title).ratio()
        score += similarity * self.weights['title_similarity']
        
        # Apply threshold penalty if similarity is too low
        if similarity < self.min_title_similarity:
            threshold_penalty = (self.min_title_similarity - similarity) * 300
            penalty -= threshold_penalty
        
        # 3. PARTIAL STRING MATCHING (Subsequence matching)
        # Check if song title words appear in order (allows for insertions)
        if song_words:
            # Sequential word matching bonus
            last_pos = -1
            sequential_matches = 0
            for word in song_words:
                pos = title_lower.find(word, last_pos + 1)
                if pos > last_pos:
                    sequential_matches += 1
                    last_pos = pos
            
            sequence_ratio = sequential_matches / len(song_words)
            score += sequence_ratio * 80  # Increased bonus for ordered appearance
            
            # Penalty if words are not in sequence
            if sequence_ratio < 0.5:
                penalty -= 100
        
        # 4. INDIVIDUAL WORD MATCHING (with position weighting)
        matched_words = 0
        for i, word in enumerate(song_words):
            if word in title_words:
                matched_words += 1
                # Extra points if word appears early in title
                if word in title_words[:5]:  # First 5 words get bonus
                    score += 15
        
        if song_words:
            word_match_ratio = matched_words / len(song_words)
            score += word_match_ratio * 100  # Increased significantly
        
        # 5. ARTIST IN TITLE (Strong signal)
        if artist_name:
            if artist_name in title:
                score += 60  # Increased
                # Bonus if artist appears early
                if title.find(artist_name) < 20:
                    score += 20
            else:
                # Partial artist name match
                artist_words = artist_name.split()
                artist_matches = sum(1 for word in artist_words if word in title)
                if artist_words:
                    partial_score = (artist_matches / len(artist_words)) * 40
                    score += partial_score
                    # Penalty if artist name not found at all
                    if artist_matches == 0:
                        penalty -= 80
        
        # 6. EXACT MATCH BONUS (Perfect title match)
        # Clean both strings and compare
        clean_song = re.sub(r'[^\w\s]', '', song_title).strip()
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        if clean_song == clean_title:
            score += 150  # MASSIVE bonus for perfect match
        
        # Check if cleaned title starts with cleaned song
        if clean_title.startswith(clean_song):
            score += 100
        
        # 7. LENGTH SIMILARITY (Prefer titles of similar length)
        length_ratio = min(len(song_title), len(title)) / max(len(song_title), len(title), 1)
        if length_ratio > 0.7:  # Similar length
            score += 30  # Increased
        
        # 8. WRONG TITLE DETECTION - Check if title contains OTHER song titles
        # This catches cases where a completely different song is returned
        if song_words and len(song_words) >= 2:
            # Get the first major word from title (likely the actual song name)
            title_first_words = ' '.join(title_words[:3])
            song_first_words = ' '.join(song_words[:2])
            
            # If title starts with completely different words, heavy penalty
            if song_first_words not in title_first_words and matched_key_words < len(song_words) * 0.4:
                penalty -= 150  # Strong penalty for wrong title
        
        return score + penalty
    
    def _score_artist_match(self, title, uploader, description, artist_name):
        """Score based on artist matching"""
        if not artist_name:
            return 0
        
        score = 0
        artist_words = artist_name.split()
        
        # Artist in uploader name (strong signal)
        if artist_name in uploader:
            score += self.weights['artist_match']
        else:
            # Partial match in uploader
            uploader_matches = sum(1 for word in artist_words if word in uploader)
            if artist_words:
                score += (uploader_matches / len(artist_words)) * self.weights['artist_match'] * 0.7
        
        # Artist in title (good signal)
        if artist_name in title:
            score += 20
        
        # Artist in description (weak signal)
        if artist_name in description[:500]:  # First 500 chars
            score += 10
        
        return score
    
    def _score_official_content(self, title, uploader, description, channel_id):
        """Score based on official/verified content indicators"""
        score = 0
        
        # Official keywords in title
        official_in_title = sum(1 for keyword in self.official_keywords if keyword in title)
        if official_in_title > 0:
            score += min(official_in_title * 15, self.weights['official_content'])
        
        # Verified channel indicators
        verified = sum(1 for keyword in self.verified_channels if keyword in uploader)
        if verified > 0:
            score += self.weights['verified_artist']
        
        # VEVO (highest authority for music)
        if 'vevo' in uploader or 'vevo' in title:
            score += 50
        
        # Official in description
        if 'official' in description[:200]:
            score += 10
        
        return score
    
    def _score_popularity(self, view_count, like_count, comment_count):
        """
        Score based on popularity metrics with mathematical precision
        Uses logarithmic scaling and polynomial interpolation for smooth gradients
        """
        score = 0
        
        # VIEWS: Hybrid scoring (logarithmic + tiered for ultra-precision)
        if view_count > 0:
            if view_count >= 1_000_000_000:  # 1B+ (viral mega-hits)
                score += self.weights['views'] * 1.0
            elif view_count >= 500_000_000:  # 500M+ (massive hits)
                score += self.weights['views'] * 0.98
            elif view_count >= 250_000_000:  # 250M+ (huge hits)
                score += self.weights['views'] * 0.95
            elif view_count >= 100_000_000:  # 100M+ (major hits)
                score += self.weights['views'] * 0.92
            elif view_count >= 75_000_000:  # 75M+
                score += self.weights['views'] * 0.88
            elif view_count >= 50_000_000:  # 50M+
                score += self.weights['views'] * 0.84
            elif view_count >= 25_000_000:  # 25M+
                score += self.weights['views'] * 0.79
            elif view_count >= 10_000_000:  # 10M+ (very popular)
                score += self.weights['views'] * 0.74
            elif view_count >= 7_500_000:  # 7.5M+
                score += self.weights['views'] * 0.69
            elif view_count >= 5_000_000:  # 5M+
                score += self.weights['views'] * 0.64
            elif view_count >= 2_500_000:  # 2.5M+
                score += self.weights['views'] * 0.59
            elif view_count >= 1_000_000:  # 1M+ (popular)
                score += self.weights['views'] * 0.54
            elif view_count >= 750_000:  # 750K+
                score += self.weights['views'] * 0.49
            elif view_count >= 500_000:  # 500K+
                score += self.weights['views'] * 0.44
            elif view_count >= 250_000:  # 250K+
                score += self.weights['views'] * 0.39
            elif view_count >= 100_000:  # 100K+ (moderate popularity)
                score += self.weights['views'] * 0.34
            elif view_count >= 75_000:  # 75K+
                score += self.weights['views'] * 0.29
            elif view_count >= 50_000:  # 50K+
                score += self.weights['views'] * 0.24
            elif view_count >= 25_000:  # 25K+
                score += self.weights['views'] * 0.19
            elif view_count >= 10_000:  # 10K+ (growing)
                score += self.weights['views'] * 0.14
            elif view_count >= 5_000:  # 5K+
                score += self.weights['views'] * 0.10
            elif view_count >= 2_500:  # 2.5K+
                score += self.weights['views'] * 0.07
            elif view_count >= 1_000:  # 1K+ (low but acceptable)
                score += self.weights['views'] * 0.05
            elif view_count >= 500:  # 500+
                score += self.weights['views'] * 0.02
            elif view_count >= 100:  # 100+
                score -= 5  # Small penalty
            else:  # Less than 100 views
                score -= 20  # Heavy penalty for extremely low views
        
        # Like count scoring (ultra-precise granular scale)
        if like_count > 0:
            if like_count >= 50_000_000:  # 50M+ (exceptional)
                score += self.weights['likes'] * 1.0
            elif like_count >= 25_000_000:  # 25M+
                score += self.weights['likes'] * 0.97
            elif like_count >= 10_000_000:  # 10M+ (massive)
                score += self.weights['likes'] * 0.94
            elif like_count >= 5_000_000:  # 5M+
                score += self.weights['likes'] * 0.90
            elif like_count >= 2_500_000:  # 2.5M+
                score += self.weights['likes'] * 0.86
            elif like_count >= 1_000_000:  # 1M+ (very high)
                score += self.weights['likes'] * 0.82
            elif like_count >= 750_000:  # 750K+
                score += self.weights['likes'] * 0.77
            elif like_count >= 500_000:  # 500K+
                score += self.weights['likes'] * 0.72
            elif like_count >= 250_000:  # 250K+
                score += self.weights['likes'] * 0.67
            elif like_count >= 100_000:  # 100K+ (high)
                score += self.weights['likes'] * 0.62
            elif like_count >= 75_000:  # 75K+
                score += self.weights['likes'] * 0.57
            elif like_count >= 50_000:  # 50K+
                score += self.weights['likes'] * 0.52
            elif like_count >= 25_000:  # 25K+
                score += self.weights['likes'] * 0.47
            elif like_count >= 10_000:  # 10K+ (good)
                score += self.weights['likes'] * 0.42
            elif like_count >= 7_500:  # 7.5K+
                score += self.weights['likes'] * 0.37
            elif like_count >= 5_000:  # 5K+
                score += self.weights['likes'] * 0.32
            elif like_count >= 2_500:  # 2.5K+
                score += self.weights['likes'] * 0.27
            elif like_count >= 1_000:  # 1K+ (moderate)
                score += self.weights['likes'] * 0.22
            elif like_count >= 500:  # 500+
                score += self.weights['likes'] * 0.17
            elif like_count >= 250:  # 250+
                score += self.weights['likes'] * 0.12
            elif like_count >= 100:  # 100+
                score += self.weights['likes'] * 0.08
            elif like_count >= 50:  # 50+
                score += self.weights['likes'] * 0.04
            elif like_count >= 10:  # 10+
                score += self.weights['likes'] * 0.01
            else:  # Less than 10 likes
                score -= 15  # Heavy penalty for extremely low likes
        
        # Comment count scoring (precise engagement indicator)
        if comment_count > 0:
            if comment_count >= 100_000:  # 100K+ comments (viral)
                score += self.weights['comment_count'] * 1.0
            elif comment_count >= 50_000:  # 50K+
                score += self.weights['comment_count'] * 0.9
            elif comment_count >= 25_000:  # 25K+
                score += self.weights['comment_count'] * 0.8
            elif comment_count >= 10_000:  # 10K+ (highly engaged)
                score += self.weights['comment_count'] * 0.7
            elif comment_count >= 5_000:  # 5K+
                score += self.weights['comment_count'] * 0.6
            elif comment_count >= 2_500:  # 2.5K+
                score += self.weights['comment_count'] * 0.5
            elif comment_count >= 1_000:  # 1K+ (good engagement)
                score += self.weights['comment_count'] * 0.4
            elif comment_count >= 500:  # 500+
                score += self.weights['comment_count'] * 0.3
            elif comment_count >= 250:  # 250+
                score += self.weights['comment_count'] * 0.2
            elif comment_count >= 100:  # 100+ (moderate)
                score += self.weights['comment_count'] * 0.15
            elif comment_count >= 50:  # 50+
                score += self.weights['comment_count'] * 0.1
            elif comment_count >= 10:  # 10+
                score += self.weights['comment_count'] * 0.05
        
        # Apply engagement quality multiplier for overall score boost
        engagement_multiplier = self._calculate_engagement_multiplier(view_count, like_count, comment_count)
        score *= engagement_multiplier
        
        return score
    
    def _calculate_logarithmic_score(self, value, max_score, scale_factor=1.0):
        """
        Calculate logarithmic score for smooth scaling
        
        Args:
            value: The metric value (views, likes, etc.)
            max_score: Maximum score this metric can achieve
            scale_factor: Scaling factor for curve adjustment
            
        Returns:
            Calculated score using logarithmic function
        """
        if value <= 0:
            return 0
        
        # Logarithmic formula: score = max_score * (log(value + 1) / log(scale_factor))
        # This provides smooth scaling across all ranges
        normalized = math.log10(value + 1) / math.log10(scale_factor + 1)
        return min(max_score * normalized, max_score)
    
    def _calculate_sigmoid_score(self, value, midpoint, max_score, steepness=1.0):
        """
        Calculate sigmoid (S-curve) score for smooth transitions
        
        Args:
            value: The metric value
            midpoint: The inflection point of the curve
            max_score: Maximum score this metric can achieve
            steepness: How steep the curve is (higher = steeper)
            
        Returns:
            Calculated score using sigmoid function
        """
        if value <= 0:
            return 0
        
        # Sigmoid formula: score = max_score / (1 + e^(-steepness * (value - midpoint)))
        try:
            sigmoid = max_score / (1 + math.exp(-steepness * (math.log10(value + 1) - math.log10(midpoint + 1))))
            return sigmoid
        except (OverflowError, ValueError):
            return max_score if value > midpoint else 0
    
    def _calculate_polynomial_score(self, value, thresholds, max_score):
        """
        Calculate score using polynomial interpolation between thresholds
        
        Args:
            value: The metric value
            thresholds: List of (threshold, score_percentage) tuples
            max_score: Maximum score this metric can achieve
            
        Returns:
            Interpolated score
        """
        if value <= 0:
            return 0
        
        # Find the appropriate threshold range
        for i in range(len(thresholds) - 1):
            if thresholds[i][0] <= value < thresholds[i + 1][0]:
                # Linear interpolation between two points
                x1, y1 = thresholds[i]
                x2, y2 = thresholds[i + 1]
                
                # Interpolation formula
                ratio = (value - x1) / (x2 - x1)
                score_percentage = y1 + (y2 - y1) * ratio
                return max_score * score_percentage
        
        # If value is beyond highest threshold
        if value >= thresholds[-1][0]:
            return max_score * thresholds[-1][1]
        
        # If value is below lowest threshold
        return max_score * thresholds[0][1]
    
    def _calculate_engagement_multiplier(self, view_count, like_count, comment_count):
        """
        Calculate a multiplier based on overall engagement quality
        
        Returns:
            Multiplier between 0.5 and 1.5
        """
        if view_count <= 0:
            return 1.0
        
        multiplier = 1.0
        
        # Like ratio impact
        if like_count > 0:
            like_ratio = like_count / view_count
            if like_ratio >= 0.10:  # Exceptional
                multiplier += 0.5
            elif like_ratio >= 0.05:  # Excellent
                multiplier += 0.3
            elif like_ratio >= 0.03:  # Good
                multiplier += 0.2
            elif like_ratio >= 0.01:  # Average
                multiplier += 0.1
            elif like_ratio < 0.001:  # Poor
                multiplier -= 0.3
        
        # Comment ratio impact
        if comment_count > 0:
            comment_ratio = comment_count / view_count
            if comment_ratio >= 0.01:  # Very engaged
                multiplier += 0.2
            elif comment_ratio >= 0.005:  # Engaged
                multiplier += 0.1
            elif comment_ratio >= 0.001:  # Some engagement
                multiplier += 0.05
        
        # Absolute engagement check (prevent low-quality viral content)
        if view_count > 100_000 and like_count < 100:
            multiplier -= 0.4  # Suspicious engagement pattern
        
        # Clamp between 0.5 and 1.5
        return max(0.5, min(1.5, multiplier))
    
    def _calculate_view_velocity_score(self, view_count, upload_date, max_score=20):
        """
        Calculate score based on views per day (trending indicator)
        
        Args:
            view_count: Total view count
            upload_date: Upload date in YYYYMMDD format
            max_score: Maximum score for this metric
            
        Returns:
            Score based on view velocity
        """
        if not upload_date or view_count <= 0:
            return 0
        
        try:
            upload_year = int(str(upload_date)[:4])
            upload_month = int(str(upload_date)[4:6])
            upload_day = int(str(upload_date)[6:8])
            
            upload_datetime = datetime(upload_year, upload_month, upload_day)
            days_since_upload = (datetime.now() - upload_datetime).days
            
            if days_since_upload <= 0:
                days_since_upload = 1  # Avoid division by zero
            
            views_per_day = view_count / days_since_upload
            
            # Score based on views per day (logarithmic)
            if views_per_day >= 1_000_000:  # Mega viral
                return max_score
            elif views_per_day >= 500_000:
                return max_score * 0.9
            elif views_per_day >= 100_000:
                return max_score * 0.8
            elif views_per_day >= 50_000:
                return max_score * 0.7
            elif views_per_day >= 10_000:
                return max_score * 0.6
            elif views_per_day >= 5_000:
                return max_score * 0.5
            elif views_per_day >= 1_000:
                return max_score * 0.4
            elif views_per_day >= 500:
                return max_score * 0.3
            elif views_per_day >= 100:
                return max_score * 0.2
            elif views_per_day >= 10:
                return max_score * 0.1
            
        except Exception:
            return 0
        
        return 0
    
    def _calculate_quality_confidence_score(self, view_count, like_count, subscriber_count):
        """
        Calculate a confidence score indicating likely video quality
        Combines multiple signals to detect authentic popular content
        
        Returns:
            Confidence multiplier (0.7 to 1.3)
        """
        confidence = 1.0
        
        # Check for organic growth patterns
        if view_count > 0 and like_count > 0:
            # Expected like ratio should be reasonable
            like_ratio = like_count / view_count
            
            # Authentic content typically has 1-10% like ratio
            if 0.01 <= like_ratio <= 0.15:
                confidence += 0.2  # Organic pattern
            elif like_ratio < 0.001:
                confidence -= 0.2  # Suspicious (bought views?)
            elif like_ratio > 0.20:
                confidence -= 0.1  # Unusual pattern
        
        # Channel authority check
        if subscriber_count > 0 and view_count > 0:
            views_to_subs_ratio = view_count / subscriber_count
            
            # Healthy ratios indicate good content
            if 0.1 <= views_to_subs_ratio <= 10:
                confidence += 0.1  # Normal ratio
            elif views_to_subs_ratio > 100:
                confidence += 0.2  # Viral hit
        
        return max(0.7, min(1.3, confidence))
    
    def _score_engagement_quality(self, view_count, like_count, comment_count):
        """Score based on engagement quality (ratios)"""
        score = 0
        
        if view_count > 0 and like_count > 0:
            like_ratio = like_count / view_count
            
            # Like ratio scoring (higher is better)
            if like_ratio >= 0.10:  # 10%+ exceptional
                score += self.weights['like_ratio']
            elif like_ratio >= 0.08:  # 8%+ excellent
                score += self.weights['like_ratio'] * 0.9
            elif like_ratio >= 0.05:  # 5%+ very good
                score += self.weights['like_ratio'] * 0.75
            elif like_ratio >= 0.03:  # 3%+ good
                score += self.weights['like_ratio'] * 0.6
            elif like_ratio >= 0.02:  # 2%+ above average
                score += self.weights['like_ratio'] * 0.45
            elif like_ratio >= 0.01:  # 1%+ average
                score += self.weights['like_ratio'] * 0.3
            elif like_ratio >= 0.005:  # 0.5%+ below average
                score += self.weights['like_ratio'] * 0.15
            else:  # Very poor engagement
                score -= 5
        
        # Comment ratio (engagement depth)
        if view_count > 0 and comment_count > 0:
            comment_ratio = comment_count / view_count
            if comment_ratio >= 0.01:  # 1%+ very engaged
                score += 15
            elif comment_ratio >= 0.005:  # 0.5%+ engaged
                score += 10
            elif comment_ratio >= 0.001:  # 0.1%+ some engagement
                score += 5
        
        return score
    
    def _score_duration(self, duration):
        """Score based on duration (music tracks have typical lengths)"""
        score = 0
        
        if duration > 0:
            # Ideal music track duration: 2-5 minutes
            if 120 <= duration <= 300:  # 2-5 minutes
                score += self.weights['duration']
            elif 90 <= duration <= 420:  # 1.5-7 minutes
                score += self.weights['duration'] * 0.8
            elif 60 <= duration <= 600:  # 1-10 minutes
                score += self.weights['duration'] * 0.5
            elif duration < 60:  # Too short
                score -= 10
            elif duration > 900:  # Too long (15+ min)
                score -= 15
        
        return score
    
    def _score_recency(self, upload_date):
        """Score based on upload date (prefer recent but not too new)"""
        if not upload_date:
            return 0
        
        try:
            # Parse upload date (format: YYYYMMDD)
            upload_year = int(str(upload_date)[:4])
            current_year = datetime.now().year
            years_ago = current_year - upload_year
            
            # Sweet spot: 0-2 years old (established but recent)
            if years_ago <= 2:
                return self.weights['recency']
            elif years_ago <= 5:
                return self.weights['recency'] * 0.8
            elif years_ago <= 10:
                return self.weights['recency'] * 0.5
            else:  # Very old
                return self.weights['recency'] * 0.3
        except:
            return 0
    
    def _score_quality_indicators(self, title, description):
        """Score based on quality indicators"""
        score = 0
        
        # Quality keywords in title
        quality_matches = sum(1 for indicator in self.quality_indicators if indicator in title)
        score += quality_matches * 10
        
        # Audio quality mentions
        if 'official audio' in title:
            score += 20
        if 'official music video' in title or 'official video' in title:
            score += 15
        if 'explicit' in title or 'clean' in title:
            score += 8
        
        # HD/4K in title
        if '4k' in title or 'uhd' in title:
            score += 12
        elif 'hd' in title or '1080p' in title:
            score += 8
        
        return score
    
    def _score_channel_authority(self, uploader, subscriber_count, channel_id):
        """Score based on channel authority and subscribers"""
        score = 0
        
        # Subscriber count scoring
        if subscriber_count > 0:
            if subscriber_count >= 10_000_000:  # 10M+ subs
                score += self.weights['subscriber_count']
            elif subscriber_count >= 5_000_000:  # 5M+ subs
                score += self.weights['subscriber_count'] * 0.85
            elif subscriber_count >= 1_000_000:  # 1M+ subs
                score += self.weights['subscriber_count'] * 0.7
            elif subscriber_count >= 500_000:  # 500K+ subs
                score += self.weights['subscriber_count'] * 0.55
            elif subscriber_count >= 100_000:  # 100K+ subs
                score += self.weights['subscriber_count'] * 0.4
            elif subscriber_count >= 10_000:  # 10K+ subs
                score += self.weights['subscriber_count'] * 0.25
            elif subscriber_count >= 1_000:  # 1K+ subs
                score += self.weights['subscriber_count'] * 0.1
        
        return score
    
    def _score_penalties(self, title, description):
        """Apply penalties for non-music content"""
        penalty = 0
        
        # Check for penalty keywords
        for keyword in self.penalty_keywords:
            if keyword in title:
                penalty -= 25  # Heavy penalty for title
            elif keyword in description[:500]:
                penalty -= 10  # Lighter penalty for description
        
        # Additional specific penalties
        if 'lyrics' in title and 'official' not in title:
            penalty -= 15  # Prefer official over lyric videos
        
        if 'live' in title and 'performance' in title:
            penalty -= 20  # Prefer studio versions
        
        if 'slowed' in title or 'reverb' in title or 'sped up' in title:
            penalty -= 30  # Heavy penalty for modified versions
        
        if 'nightcore' in title or '8d audio' in title:
            penalty -= 35  # Very heavy penalty for fan edits
        
        return penalty
    
    def _score_description(self, description, song_title, artist_name):
        """Score based on description relevance"""
        score = 0
        
        # Check first 500 characters (most relevant part)
        desc_start = description[:500]
        
        # Song title in description
        if song_title in desc_start:
            score += 10
        
        # Artist in description
        if artist_name and artist_name in desc_start:
            score += 10
        
        # Professional description indicators
        professional_indicators = [
            'listen to', 'stream', 'download', 'available now',
            'out now', 'new album', 'spotify', 'apple music',
            'follow me', 'subscribe', 'connect with'
        ]
        
        matches = sum(1 for indicator in professional_indicators if indicator in desc_start)
        score += matches * 3
        
        return score
    
    def _print_breakdown(self, breakdown, total_score, video_info):
        """Print detailed scoring breakdown with enhanced metrics"""
        title = video_info.get('title', 'Unknown')
        view_count = video_info.get('view_count', 0) or 0
        like_count = video_info.get('like_count', 0) or 0
        comment_count = video_info.get('comment_count', 0) or 0
        upload_date = video_info.get('upload_date', '')
        
        print(f"\n  📊 Advanced Scoring Breakdown for: {title[:60]}...")
        print(f"  " + "═" * 80)
        
        # Group scores by category
        content_scores = {}
        engagement_scores = {}
        quality_scores = {}
        
        for category, score in breakdown.items():
            if category in ['title_match', 'artist_match', 'official_content', 'description']:
                content_scores[category] = score
            elif category in ['popularity', 'engagement_quality', 'like_ratio', 'combined_engagement', 'view_velocity']:
                engagement_scores[category] = score
            else:
                quality_scores[category] = score
        
        # Print content relevance scores
        if content_scores:
            print(f"  🎵 Content Relevance:")
            for category, score in content_scores.items():
                category_display = category.replace('_', ' ').title()
                bar_length = int((abs(score) / max(1, total_score)) * 25)
                bar = '█' * bar_length
                sign = '+' if score >= 0 else ''
                print(f"    {category_display:.<28} {sign}{score:>7.1f} {bar}")
        
        # Print engagement scores
        if engagement_scores:
            print(f"\n  🔥 Engagement Metrics:")
            for category, score in engagement_scores.items():
                category_display = category.replace('_', ' ').title()
                bar_length = int((abs(score) / max(1, total_score)) * 25)
                bar = '█' * bar_length
                sign = '+' if score >= 0 else ''
                print(f"    {category_display:.<28} {sign}{score:>7.1f} {bar}")
        
        # Print quality scores
        if quality_scores:
            print(f"\n  ⭐ Quality Indicators:")
            for category, score in quality_scores.items():
                category_display = category.replace('_', ' ').title()
                if category == 'quality_confidence':
                    # Display as multiplier
                    print(f"    {category_display:.<28} {'×'}{score:>7.2f}")
                else:
                    bar_length = int((abs(score) / max(1, total_score)) * 25)
                    bar = '█' * bar_length
                    sign = '+' if score >= 0 else ''
                    print(f"    {category_display:.<28} {sign}{score:>7.1f} {bar}")
        
        print(f"  " + "═" * 80)
        print(f"  {'🏆 FINAL SCORE':.<30} {total_score:>7.1f}")
        print(f"  " + "═" * 80)
        
        # Calculate and display engagement ratios
        like_ratio = (like_count / view_count * 100) if view_count > 0 else 0
        comment_ratio = (comment_count / view_count * 100) if view_count > 0 else 0
        
        # Calculate view velocity if upload date available
        velocity_info = ""
        if upload_date:
            try:
                upload_year = int(str(upload_date)[:4])
                upload_month = int(str(upload_date)[4:6])
                upload_day = int(str(upload_date)[6:8])
                upload_datetime = datetime(upload_year, upload_month, upload_day)
                days_since = (datetime.now() - upload_datetime).days
                if days_since > 0:
                    views_per_day = view_count / days_since
                    velocity_info = f" | Velocity: {views_per_day:,.0f} views/day"
            except:
                pass
        
        print(f"  📈 Views: {view_count:,} | 👍 Likes: {like_count:,} ({like_ratio:.2f}%)")
        print(f"  💬 Comments: {comment_count:,} ({comment_ratio:.3f}%){velocity_info}")
        print()


# Convenience function for easy import
def score_youtube_video(video_info, query, verbose=False):
    """
    Score a YouTube video for music search relevance
    
    Args:
        video_info: Dictionary with video metadata from yt-dlp
        query: Search query in "Title - Artist" format
        verbose: Print detailed breakdown
        
    Returns:
        tuple: (total_score, breakdown_dict)
    """
    scorer = YouTubeScorer()
    return scorer.score_video(video_info, query, verbose)
