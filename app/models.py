from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    avatar_url = fields.CharField(max_length=255, null=True)

    role = fields.CharField(max_length=50, default="user")  # 新增角色字段，默认普通用户


    def __str__(self):
        return self.username

User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Tag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField()
    def __str__(self):
        return self.name

class Article(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="articles")
    is_published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 分类+标签
    category = fields.ForeignKeyField("models.Category", related_name="articles")
    tag = fields.ManyToManyField("models.Tag", related_name="articles", through="article_tag")


    def __str__(self):
        return self.title

Category_Pydantic = pydantic_model_creator(Category, name="Category")
CategoryIn_Pydantic = pydantic_model_creator(Category, name="CategoryIn", exclude_readonly=True)

Tag_Pydantic = pydantic_model_creator(Tag, name="Tag")
TagIn_Pydantic = pydantic_model_creator(Tag, name="TagIn", exclude_readonly=True)

Article_Pydantic = pydantic_model_creator(Article, name="Article")
ArticleIn_Pydantic = pydantic_model_creator(Article, name="ArticleIn", exclude_readonly=True)


class Comment(models.Model):
    id = fields.IntField(pk=True)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="comments")
    article = fields.ForeignKeyField("models.Article", related_name="comments")
    is_visible = fields.BooleanField(default=True)  # 审核/屏蔽
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    is_approved = fields.BooleanField(default=False)  # 是否审核通过

    def __str__(self):
        return f"Comment {self.id} by {self.author.username}"

Comment_Pydantic = pydantic_model_creator(Comment, name="Comment")
CommentIn_Pydantic = pydantic_model_creator(Comment, name="CommentIn", exclude_readonly=True)

class ArticleLike(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="article_likes")
    article = fields.ForeignKeyField("models.Article", related_name="likes")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")  # 同一个用户只能点赞一次

class CommentLike(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="comment_likes")
    comment = fields.ForeignKeyField("models.Comment", related_name="likes")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")

class ArticleFavorite(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="favorites")
    article = fields.ForeignKeyField("models.Article", related_name="favorites")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")

# 金融资讯模型
class FinancialNews(models.Model):
    """金融信息"""
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="financial_news")
    is_published = fields.BooleanField(default=False)
    # 无需在代码中处理时间戳，ORM 会自动维护
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    news_type = fields.CharField(max_length=50, default="general")
    symbol = fields.CharField(max_length=50, null=True)
    sentiment_score = fields.FloatField(null=True)
    source_url = fields.CharField(max_length=500, null=True)

# 市场数据模型
class MarketData(models.Model):
    """市场数据"""
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=50)
    name = fields.CharField(max_length=255)
    current_price = fields.DecimalField(max_digits=15, decimal_places=4)
    change_percent = fields.DecimalField(max_digits=15, decimal_places=4)
    volume = fields.BigIntField()
    market_type = fields.CharField(max_length=50)
    updated_at = fields.DatetimeField(auto_now=True)

# AI分析结果模型
class SentimentAnalysis(models.Model):
    """市场情绪分析结果"""
    id = fields.IntField(pk=True)
    symbol = fields.CharField(max_length=20)
    analysis_date = fields.DatetimeField(auto_now_add=True)
    sentiment_score = fields.FloatField()  # -1 (极度悲观) 到 1 (极度乐观)
    confidence = fields.FloatField()  # 0-1, 分析置信度
    summary = fields.TextField()  # AI生成的情绪分析摘要
    news_count = fields.IntField(default=0)  # 分析的新闻数量

