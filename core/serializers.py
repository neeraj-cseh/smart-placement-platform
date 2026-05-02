from rest_framework import serializers
from .models import Track, Topic, Question, Test, CodeSubmission, InterviewSession, InterviewQA


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'name', 'description']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'order', 'is_active']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id',
            'question_text',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'difficulty',
        ]


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'duration_minutes', 'questions']


class TestSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'name', 'description', 'duration_minutes']


class CodeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSubmission
        fields = ['id', 'code', 'language', 'output', 'error_output', 'execution_time_ms', 'memory_kb', 'stdin', 'created_at']
        read_only_fields = ['output', 'error_output', 'execution_time_ms', 'memory_kb', 'created_at']


class InterviewQASerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQA
        fields = ['id', 'question', 'user_answer', 'ai_feedback', 'score', 'max_score', 'created_at']


class InterviewSessionSerializer(serializers.ModelSerializer):
    qa_pairs = InterviewQASerializer(many=True, read_only=True)

    class Meta:
        model = InterviewSession
        fields = ['id', 'category', 'current_question_index', 'total_questions', 'status', 'score', 'max_score', 'started_at', 'completed_at', 'qa_pairs']
