from django.db import models
from django.core.validators import MinLengthValidator


class Track(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='topics', null=True, blank=True)

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, null=True, blank=True, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    DOMAIN_CHOICES = (
        ('dsa', 'Data Structures & Algorithms'),
        ('aptitude', 'Aptitude & Logical'),
        ('core_cs', 'Core Computer Science'),
        ('career', 'Career & Behavioral'),
    )
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES, default='dsa')
    
    interview_frequency = models.CharField(max_length=50, default="Medium")
    target_companies = models.JSONField(default=list, blank=True)
    why_it_matters = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('track', 'order', 'id')

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(self.name)
            self.slug = base_slug if base_slug else str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        track_name = self.track.name if self.track else "General"
        return f"{track_name} - {self.name}"


class TopicDependency(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='dependencies')
    prerequisite = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='prerequisites_for')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['topic', 'prerequisite'], name='unique_topic_prerequisite')
        ]

    def __str__(self):
        return f"{self.prerequisite.name} -> {self.topic.name}"


class TopicSection(models.Model):
    SECTION_TYPE_CHOICES = (
        ('overview', 'Overview'),
        ('learn', 'Learn'),
        ('guided', 'Guided Examples'),
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=180)
    content_markdown = models.TextField()
    section_type = models.CharField(max_length=20, choices=SECTION_TYPE_CHOICES, default='overview')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('order', 'id')

    def __str__(self):
        return f"{self.topic.name} - {self.section_type} - {self.title}"


class TopicVisualization(models.Model):
    VIS_TYPE_CHOICES = (
        ('sliding-window', 'Sliding Window'),
        ('graph-dfs', 'Graph DFS/BFS'),
        ('linked-list-cycle', 'Linked List Cycle'),
        ('aptitude-profit', 'Aptitude Profit/Loss'),
        ('generic', 'Generic'),
    )
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='visualization')
    title = models.CharField(max_length=180, default="Interactive Visualization")
    visualization_type = models.CharField(max_length=30, choices=VIS_TYPE_CHOICES, default='generic')
    config_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Vis: {self.topic.name} ({self.visualization_type})"


class TopicRevision(models.Model):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, related_name='revision')
    key_takeaways = models.JSONField(default=list, blank=True)
    cheat_sheet_markdown = models.TextField(blank=True)

    def __str__(self):
        return f"Revision: {self.topic.name}"


class UserTopicProgress(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='topic_progress')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_progress')

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'topic'], name='unique_user_topic_progress')
        ]
        indexes = [
            models.Index(fields=['user', 'is_completed'], name='idx_user_completed'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.topic.name}"


class Question(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')

    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(max_length=1, validators=[MinLengthValidator(1)])

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    explanation = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('topic', 'id')

    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"


class UserAnswer(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')

    selected_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', 'is_correct'], name='idx_user_correct'),
            models.Index(fields=['user', 'question'], name='idx_user_question'),
            models.Index(fields=['created_at'], name='idx_created_at'),
        ]

    def __str__(self):
        return f"{self.user.email} - Q{self.question.id}"


class Test(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    topics = models.ManyToManyField(Topic, related_name='tests')
    questions = models.ManyToManyField(Question, related_name='tests')

    duration_minutes = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TestAttempt(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-started_at',)
        indexes = [
            models.Index(fields=['user', 'completed_at'], name='idx_user_completed_attempts'),
            models.Index(fields=['user', 'test'], name='idx_user_test'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.test.name}"


class DailyPlanItem(models.Model):
    TONE_CHOICES = (
        ('cyan', 'Cyan'),
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
        ('violet', 'Violet'),
        ('slate', 'Slate'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='daily_plan_items')

    title = models.CharField(max_length=180)
    detail = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=80, blank=True)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='cyan')

    date = models.DateField()
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date', 'order', 'id')

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class CompanyTarget(models.Model):
    TONE_CHOICES = (
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
        ('slate', 'Slate'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='company_targets')

    name = models.CharField(max_length=120)
    readiness_percentage = models.PositiveSmallIntegerField(default=0)
    focus = models.CharField(max_length=180, blank=True)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='slate')
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', 'name')
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_user_active_company'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class RevisionQueueItem(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='revision_queue_items')

    title = models.CharField(max_length=180)
    cycle_label = models.CharField(max_length=50)
    duration_minutes = models.PositiveSmallIntegerField(default=10)
    due_date = models.DateField()
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('due_date', 'order', 'id')

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class InterviewReadiness(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='interview_readiness_items')

    area = models.CharField(max_length=80)
    score = models.PositiveSmallIntegerField(default=0)
    max_score = models.PositiveSmallIntegerField(default=10)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', 'area')

    def __str__(self):
        return f"{self.user.email} - {self.area}"


class ActivityEvent(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='activity_events')

    event_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    occurred_at = models.DateTimeField()
    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-occurred_at', '-id')
        indexes = [
            models.Index(fields=['user', '-occurred_at'], name='idx_user_activity'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.event_type}"





class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('sql', 'SQL'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='code_submissions')
    problem = models.ForeignKey('CodingProblem', on_delete=models.CASCADE, related_name='submissions', null=True, blank=True)

    code = models.TextField()
    language = models.CharField(max_length=15, choices=LANGUAGE_CHOICES, default='python')
    output = models.TextField(blank=True, null=True)
    error_output = models.TextField(blank=True, null=True)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    memory_kb = models.IntegerField(null=True, blank=True)
    stdin = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="Accepted") # Accepted, Wrong Answer, TLE, MLE, Runtime Error
    attempt_number = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_user_code_subs'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.language} ({self.created_at})"


class InterviewSession(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='interview_sessions')

    category = models.CharField(max_length=50, default='general')
    current_question_index = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=5)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-started_at',)

    def __str__(self):
        return f"{self.user.email} - {self.category} ({self.status})"


class InterviewQA(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='qa_pairs')

    question = models.TextField()
    user_answer = models.TextField()
    ai_feedback = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QA #{self.id} (Session {self.session_id})"


class UserDraft(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='drafts')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_drafts')
    exercise_id = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'topic', 'exercise_id')

    def __str__(self):
        return f"{self.user.username} - {self.topic.slug} - {self.exercise_id}"


class UserResume(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='resume')
    file_name = models.CharField(max_length=255, default="my_resume.pdf")
    uploaded_at = models.DateTimeField(auto_now=True)
    overall_score = models.IntegerField(default=68)
    ats_score = models.IntegerField(default=65)
    recruiter_score = models.IntegerField(default=62)
    analysis_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.email} - {self.file_name} ({self.overall_score}%)"


class UserPassport(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='passport')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Core scores
    employability_score = models.IntegerField(default=74)
    competency_score = models.IntegerField(default=78)
    recruiter_trust_score = models.CharField(max_length=20, default="High")
    readiness_tier = models.CharField(max_length=50, default="Product Company Ready")

    # JSON storage for skills graph, validated credentials, evidence timeline, and copilot roadmaps
    passport_data = models.JSONField(default=dict)

    # Public profile sharing
    is_public = models.BooleanField(default=True)
    public_token = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        import uuid
        if not self.public_token:
            self.public_token = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - Passport ({self.employability_score}%)"


class UserCertificate(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='certificates')
    skill_name = models.CharField(max_length=100)
    skill_score = models.IntegerField(default=75)
    trust_score = models.IntegerField(default=80)
    readiness_level = models.CharField(max_length=50, default="High Confidence")
    verification_date = models.DateField(auto_now_add=True)
    certificate_id = models.CharField(max_length=100, unique=True)
    cryptographic_hash = models.CharField(max_length=100, unique=True)
    
    # Validation evidence and pressure-test stats
    evidence_data = models.JSONField(default=dict)
    
    # Sharing & security
    is_public = models.BooleanField(default=True)
    sharing_token = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        import uuid
        import random
        if not self.certificate_id:
            self.certificate_id = f"CERT-{self.skill_name[:3].upper()}-{random.randint(1000, 9999)}"
        if not self.cryptographic_hash:
            self.cryptographic_hash = f"sha256-{uuid.uuid4().hex[:12]}"
        if not self.sharing_token:
            self.sharing_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.skill_name} - {self.certificate_id}"


class UserProject(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField()
    domain = models.CharField(max_length=100)
    tech_stack = models.JSONField(default=list)
    difficulty = models.CharField(max_length=50, default="Medium")
    status = models.CharField(max_length=50, default="Active") # Generated, Active, Completed, Evaluated
    
    # guided workspace fields
    milestones = models.JSONField(default=list)
    kanban_board = models.JSONField(default=dict)
    
    # evaluation fields
    impact_scores = models.JSONField(default=dict)
    evaluation_report = models.JSONField(default=dict)
    
    # URLs and diagrams
    deployment_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    architecture_diagram = models.TextField(blank=True, null=True)
    
    # sync to resume
    resume_sync_status = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Project: {self.title}"


class UserPortfolio(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='portfolio')
    portfolio_strength = models.IntegerField(default=75)
    recruiter_attractiveness = models.IntegerField(default=70)
    competitiveness_score = models.IntegerField(default=68)
    selected_template = models.CharField(max_length=100, default="SDE Portfolio")
    public_url_slug = models.CharField(max_length=100, unique=True, blank=True)
    is_public = models.BooleanField(default=True)
    
    # analytics tracking
    analytics = models.JSONField(default=dict)
    
    # Copilot recommendations
    copilot_advice = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.public_url_slug:
            import uuid
            self.public_url_slug = f"portfolio-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - Portfolio ({self.portfolio_strength}%)"


class CodingProblem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    difficulty = models.CharField(max_length=20, default="Easy") # Easy, Medium, Hard
    topics = models.JSONField(default=list) # ["Arrays", "HashMap"]
    companies = models.JSONField(default=list) # ["Google", "Amazon"]
    relevance_score = models.IntegerField(default=90) # Interview frequency percentage
    readiness_impact = models.IntegerField(default=3) # Score added to profile (e.g. +3% SDE readiness)
    acceptance_rate = models.FloatField(default=50.0) # Acceptance rate percentage
    function_name = models.CharField(max_length=100, default="solve", help_text="Name of the function to call in the runner")
    
    description = models.TextField() # Markdown description
    constraints = models.JSONField(default=list) # ["O(n) time constraint", "nums.length <= 10^5"]
    examples = models.JSONField(default=list) # [{"input": "...", "output": "...", "explanation": "..."}]
    hints = models.JSONField(default=list) # ["Consider using a two-pointer approach..."]
    
    # Starter code templates
    starter_code = models.JSONField(default=dict) # {"python": "def twoSum(nums, target):\n    pass", "javascript": "..."}
    function_signature = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.difficulty} - {self.title} ({self.id})"

    @property
    def testcases(self):
        import json
        tcs = []
        for tc in self.test_cases.all():
            inp = tc.input_data
            if not isinstance(inp, str):
                if isinstance(inp, dict):
                    formatted_vals = []
                    for v in inp.values():
                        if isinstance(v, list):
                            formatted_vals.append(" ".join(map(str, v)))
                        else:
                            formatted_vals.append(str(v))
                    inp_str = "\n".join(formatted_vals)
                elif isinstance(inp, list):
                    inp_str = " ".join(map(str, inp))
                else:
                    inp_str = str(inp)
            else:
                inp_str = inp

            exp = tc.expected_output
            if not isinstance(exp, str):
                if isinstance(exp, list):
                    exp_str = " ".join(map(str, exp)) + "\n"
                else:
                    exp_str = str(exp) + "\n"
            else:
                exp_str = exp

            tcs.append({
                "input": inp_str,
                "expected": exp_str,
                "is_hidden": tc.is_hidden
            })
        return tcs



class TestCase(models.Model):
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.JSONField()
    expected_output = models.JSONField()
    is_hidden = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f"Test Case {self.id} for {self.problem.slug}"


class CodingContest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    problems = models.ManyToManyField(CodingProblem, related_name='contests', blank=True)
    is_active = models.BooleanField(default=True)
    platform = models.CharField(max_length=100, default='PrepSmart')
    external_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
class CodeSnippet(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='snippets')
    title = models.CharField(max_length=255)
    code = models.TextField()
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.language}) - {self.user.email}"


class UserProblemBookmark(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='bookmarked_problems')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'problem')

    def __str__(self):
        return f"{self.user.email} bookmarked {self.problem.slug}"

