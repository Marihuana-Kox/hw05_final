from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=130, unique=True)
    description = models.TextField("Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField("Название текста", max_length=100, default="Название текста")
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)  # поле для картинки
    index_page = models.CharField(max_length=512, blank=True, db_index=True)

    def __str__(self):
        return (self.title, self.pk)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_comment")
    text = models.TextField() 
    created = models.DateTimeField("date comment", auto_now_add=True)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower") 
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following") 

    class Meta:
        unique_together=['user', 'author']