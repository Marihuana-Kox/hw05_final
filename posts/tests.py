from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.http import response


class TestStringMethods(TestCase):
    userBy = {'username': 'testuser', 'email': 'testuser@user.com',
              'password': 'Fa123456', 'password1': 'Fa123456', 'password2': 'Fa123456'}
    userDy = {'username': 'testuser_d', 'email': 'testuser@user.com',
              'password': 'Fa123456', 'password1': 'Fa123456', 'password2': 'Fa123456'}
    test_post = 'Задача организации, в особенности же сложившаяся структура'
    test_post_d = 'Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок'
    comment = 'My best comment!'

    def setUp(self):
        self.client = Client()
        response = self.client.post(
            reverse("signup"), self.userBy, follow=True)
        self.assertRedirects(response, "/auth/login/",
                             status_code=302, target_status_code=200)
        User.objects.get(username=self.userBy['username'])
        self.assertRedirects(response, "/auth/login/",
                             status_code=302, target_status_code=200)
        print("Новый пользователь создан")
        response = self.client.post(
            "/auth/login/", {'username': 'testuser', 'password': 'Fa123456'})
        print("Пользователь авторизован")

        with open("media/posts/14.jpg", "rb") as fp:
            response = self.client.post(
                reverse("new_post"), {'text': self.test_post, 'image': fp})
        self.assertRedirects(response, reverse("index"), status_code=302,
                             target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        print("Пользователь создал пост")
        response = self.client.post(
            reverse("signup"), self.userDy, follow=True)
        self.assertRedirects(response, "/auth/login/",
                             status_code=302, target_status_code=200)
        print("Второй пользователь создан")
        self.client.post(
            "/auth/login/", {'username': 'testuser_d', 'password': 'Fa123456'})
        print("Второй пользователь авторизован")

        response = self.client.post(
            reverse("new_post"), {'text': self.test_post_d})
        self.assertRedirects(response, reverse("index"), status_code=302,
                             target_status_code=200, msg_prefix='', fetch_redirect_response=True)

        self.client.post(reverse("post", kwargs={
                         'username': self.userBy['username'], 'post_id': 1}), {'text': self.comment})

    def test_add_new_user(self):

        response = self.client.get(
            reverse("profile", kwargs={"username": self.userDy['username']}))
        self.assertContains(response, self.test_post_d, count=1,
                            status_code=200, msg_prefix='Поста на profile странице нет АВТОРА')
        print("Пост на profile странице АВТОРА")

        response = self.client.get("/testuser/follow", follow=True)
        print("Подписка на АВТОРА")
        self.assertRedirects(response, reverse("follow_index"),
                             status_code=302, target_status_code=200)

        response = self.client.get(reverse("follow_index"))
        self.assertContains(response, self.test_post, count=1,
                            status_code=200, msg_prefix='Поста на follow_index странице нет')
        print("Пост на follow_index странице USERA")

        response = self.client.get(reverse("post", kwargs={
            'username': self.userBy['username'], 'post_id': 1}))

        self.assertContains(response, self.test_post, count=1, status_code=200,
                            msg_prefix='Поста на post странице нет')
        print("Пост на странице POST USERA")

        self.assertContains(response,  self.comment, count=1, status_code=200,
                            msg_prefix='Комментария на post странице нет')
        print("Коментарий на странице POST USERA")

    def test_no_picture_ban(self):
        with open("media/posts/no_image.txt", "rb") as fp:
            response = self.client.post(
                reverse("new_post"), {'text': self.test_post, 'image': fp})

    def test_index_img_show(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, '<img', count=1, status_code=200,
                            msg_prefix='Картинки на главной странице нет')
        print("Картинка на главной странице, имеется")

    def test_profile_img_show(self):
        response = self.client.get(
            reverse("profile", kwargs={'username': self.userBy['username']}))
        self.assertContains(response, '<img', count=1, status_code=200,
                            msg_prefix='Картинки на profile странице нет')
        print("Картинка на profile странице, имеется")

    def test_not_found(self):
        response = self.client.get("/not_fount/")
        self.assertEqual(response.status_code, 404)

    def test_send_mail(self):
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'Тема письма')
        print("Письмо отправлено")

    def test_view_new_post_Page(self):
        response = self.client.get(reverse("new_post"))
        self.assertEqual(response.status_code, 200)
        print("Доступ к странице добавления поста, есть!")

    def test_view_index_page(self):
        response = self.client.get(reverse("index"))
        self.assertContains(response, self.test_post, count=1,
                            status_code=200, msg_prefix='Поста на главной странице нет')
        print("Пост на главной странице")

    def test_view_profile_page(self):
        response = self.client.get(
            reverse("profile", kwargs={'username': self.userBy['username']}))
        self.assertContains(response, self.test_post, count=1,
                            status_code=200, msg_prefix='Поста profile на странице нет')
        print("Пост на profile странице")

    def test_view_edit_page(self):
        self.client.post(reverse("post_edit", kwargs={
                         'username': self.userBy['username'], 'post_id': 1}), {'text': 'My best Editen text!'})
        print("Страница поста редактирования")
        response = self.client.get(
            reverse("post", kwargs={'username': self.userBy['username'], 'post_id': 1}))
        self.assertContains(response, 'My best Editen text!', count=1,
                            status_code=200, msg_prefix='Поста на главной странице нет', html=False)
        print("Отредактированый пост на главной странице")

    def test_cache_view(self):
        self.client.post(reverse("post_edit", kwargs={
                         'username': self.userBy['username'], 'post_id': 1}), {'text': 'My best Editen text!'})
        response = self.client.get(
            reverse("post", kwargs={'username': self.userBy['username'], 'post_id': 1}))
        self.assertContains(response, 'My best Editen text!', count=1,
                            status_code=200, msg_prefix='Поста на post странице нет', html=False)
        print("Отредактированый пост на post странице минуя кеш")
        response = self.client.get(reverse("index"))
        self.assertContains(response, 'My best Editen text!', count=0)
        print(
            "Отредактированый пост на главной странице не отображается, кешируется старый")


class TestNotViewPage(TestCase):
    def test_access_ban_add_new_post(self):
        response = self.client.get(reverse("new_post"))
        self.assertEqual(response.status_code, 302)
        print("Страница добавления поста недоступна")

    def test_access_ban_user_edit_post(self):
        response = self.client.get(f"/testuser/1/edit/")
        self.assertEqual(response.status_code, 302)
        print("Страница поста редактирования недоступна")
