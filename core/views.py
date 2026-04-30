from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from .models import Track, Topic, UserTopicProgress, Question, UserAnswer, Test, TestAttempt
from .serializers import TrackSerializer, TopicSerializer, QuestionSerializer, TestSerializer
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Question


class TrackListView(APIView):
    def get(self, request):
        tracks = Track.objects.all()
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)


class TopicByTrackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, track_id):
        topics = Topic.objects.filter(track_id=track_id).order_by('order')

        response_data = []

        for topic in topics:
            progress = UserTopicProgress.objects.filter(
                user=request.user,
                topic=topic,
                is_completed=True
            ).first()

            response_data.append({
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "order": topic.order,
                "is_completed": True if progress else False
            })

        return Response(response_data)

# ✅ NEW
class CompleteTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic_id=topic_id
        )

        progress.is_completed = True
        progress.save()

        return Response({
            "message": "Topic marked as completed"
        })
    
class TrackProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, track_id):
        total_topics = Topic.objects.filter(track_id=track_id).count()

        completed_topics = UserTopicProgress.objects.filter(
            user=request.user,
            topic__track_id=track_id,
            is_completed=True
        ).count()

        progress = 0
        if total_topics > 0:
            progress = (completed_topics / total_topics) * 100

        return Response({
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "progress_percentage": round(progress, 2)
        })
    
class QuestionByTopicView(APIView):
    def get(self, request, topic_id):
        questions = Question.objects.filter(topic_id=topic_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        user_answer = request.data.get("answer")

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        is_correct = (user_answer == question.correct_answer)

        # ✅ SAVE USER ANSWER
        UserAnswer.objects.create(
            user=request.user,
            question=question,
            selected_answer=user_answer,
            is_correct=is_correct
        )

        return Response({
            "correct": is_correct
        })
    
class WeakTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        topics = Topic.objects.all()

        weak_topics = []

        for topic in topics:
            total = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic
            ).count()

            if total == 0:
                continue

            correct = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).count()

            accuracy = (correct / total) * 100

            if accuracy < 50:
                weak_topics.append({
                    "topic": topic.name,
                    "accuracy": round(accuracy, 2)
                })

        return Response(weak_topics)
    
class TestDetailView(APIView):
    def get(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=404)

        serializer = TestSerializer(test)
        return Response(serializer.data)

from rest_framework.permissions import IsAuthenticated

class StartTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=404)

        attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            total_questions=test.questions.count()
        )

        return Response({
            "message": "Test started",
            "attempt_id": attempt.id,
            "total_questions": attempt.total_questions
        })

from django.utils import timezone

class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        attempt_id = request.data.get("attempt_id")
        answers = request.data.get("answers", {})

        try:
            attempt = TestAttempt.objects.get(id=attempt_id, user=request.user)
        except TestAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=404)

        score = 0
        detailed_result = []

        for q_id, user_ans in answers.items():
            try:
                question = Question.objects.get(id=q_id)
            except Question.DoesNotExist:
                continue

            is_correct = (user_ans == question.correct_answer)

            if is_correct:
                score += 1

            detailed_result.append({
                "question_id": q_id,
                "your_answer": user_ans,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct
            })

        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "score": score,
            "total": attempt.total_questions,
            "results": detailed_result
        })
    
class TopicAccuracyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        topics = Topic.objects.all()
        result = []

        for topic in topics:
            total = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic
            ).count()

            if total == 0:
                continue

            correct = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).count()

            accuracy = (correct / total) * 100

            result.append({
                "topic": topic.name,
                "accuracy": round(accuracy, 2)
            })

        return Response(result)
    
class OverallPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = UserAnswer.objects.filter(user=request.user).count()

        correct = UserAnswer.objects.filter(
            user=request.user,
            is_correct=True
        ).count()

        accuracy = 0
        if total > 0:
            accuracy = (correct / total) * 100

        return Response({
            "total_attempts": total,
            "correct_answers": correct,
            "accuracy": round(accuracy, 2)
        })
    
class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        # 🔹 Overall Performance
        total = UserAnswer.objects.filter(user=request.user).count()
        correct = UserAnswer.objects.filter(
            user=request.user,
            is_correct=True
        ).count()

        overall_accuracy = 0
        if total > 0:
            overall_accuracy = (correct / total) * 100

        overall_data = {
            "total_attempts": total,
            "correct_answers": correct,
            "accuracy": round(overall_accuracy, 2)
        }

        # 🔹 Topic-wise Accuracy
        topics = Topic.objects.all()
        topic_data = []

        for topic in topics:
            t_total = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic
            ).count()

            if t_total == 0:
                continue

            t_correct = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).count()

            t_accuracy = (t_correct / t_total) * 100

            topic_data.append({
                "topic": topic.name,
                "accuracy": round(t_accuracy, 2)
            })

        # 🔹 Weak Topics (<50%)
        weak_topics = [
            t for t in topic_data if t["accuracy"] < 50
        ]

        return Response({
            "overall": overall_data,
            "topics": topic_data,
            "weak_topics": weak_topics
        })
    
class AIExplanationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question_id = request.data.get("question_id")

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        # ⚠️ TEMP FAKE AI (we upgrade later)
        explanation = f"The correct answer is {question.correct_answer}. This is because of standard concept related to the topic."

        return Response({
            "question": question.question_text,
            "correct_answer": question.correct_answer,
            "explanation": explanation
        })
    
