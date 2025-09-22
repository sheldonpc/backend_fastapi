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