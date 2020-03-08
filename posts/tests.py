from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.http import response
from django.contrib.auth import logout
from django.core.cache import cache

""" С fixtures я не смог разобратся, написано что это очень просто но у меня не получиолось
буду благодарен за мастеокласс по этому модулю """

USER_BY = {'username': 'testuser', 'email': 'testuser@user.com',
           'password': 'Fa123456', 'password1': 'Fa123456', 'password2': 'Fa123456'}
USER_DY = {'username': 'testuser_d', 'email': 'testuser@user.com',
           'password': 'Fa123456', 'password1': 'Fa123456', 'password2': 'Fa123456'}
TEST_POST = 'Задача организации, в особенности же сложившаяся структура'
TEST_POST_D = 'Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок'
COMMENT = 'My best comment!'


class TestStringMethods(TestCase):

    def setUp(self):
        """Создание пользователя, авторизация и добавление поста с проверкой на главной странице"""
        self.client = Client()
        response = self.client.post(reverse("signup"), USER_BY, follow=True)
        self.assertRedirects(response, reverse("login"),
                             status_code=302, target_status_code=200)
        print("Новый пользователь создан")
        response = self.client.post(
            "/auth/login/", {'username': USER_BY['username'], 'password': USER_BY['password']})
        print("Пользователь авторизован")
        self.client.post(reverse("new_post"), {'text': TEST_POST})
        cache.clear()
        response = self.client.get(reverse("index"))
        self.assertContains(response, TEST_POST, count=1,
                            status_code=200, msg_prefix='Поста на INDEX странице нет')
        print("Создан пост на главной странице")

    def test_add_img(self):
        """Создание поста с картинкой"""
        with open("test_files/image.png", "rb") as fp:
            response = self.client.post(
                reverse("new_post"), {'text': TEST_POST_D, 'image': fp})
        self.assertRedirects(response, reverse("index"), status_code=302,
                             target_status_code=200, msg_prefix='', fetch_redirect_response=True)
        print("Пользователь создал пост С КАРТИНКОЙ")

    def test_add_new_user(self):
        """Создание второго пользователя, авторизация, подписка на первого и добавление коментария"""
        response = self.client.post(
            reverse("signup"), USER_DY, follow=True)
        self.assertRedirects(response, "/auth/login/",
                             status_code=302, target_status_code=200)
        print("Второй пользователь создан")
        self.client.post(
            "/auth/login/", {'username': 'testuser_d', 'password': 'Fa123456'})
        print("Второй пользователь авторизован")

        response = self.client.post(reverse("profile_follow", kwargs={
                                    'username': USER_BY['username']}), follow=True)
        print("Подписка на АВТОРА")
        self.assertRedirects(response, reverse("follow_index"),
                             status_code=302, target_status_code=200)

        response = self.client.get(reverse("follow_index"))
        self.assertContains(response, TEST_POST, count=1,
                            status_code=200, msg_prefix='Поста на follow_index странице нет')
        print("Пост на follow_index странице USERA")

        self.client.post(reverse("add_comment", kwargs={
                         'username': USER_BY['username'], 'post_id': 1}), {'text': COMMENT})
        response = self.client.get("/testuser/1/", follow=True)
        self.assertContains(response,  COMMENT, count=1, status_code=200,
                            msg_prefix='Комментария на post странице нет')
        print("Коментарий на странице POST USERA")

    def test_no_picture_ban(self):
        """Добавление не картинки, к посту"""
        with open("test_files/test_file.txt", "rb") as fp:
            response = self.client.post(
                reverse("new_post"), {'text': TEST_POST, 'image': fp})
        response = self.client.get(reverse("index"))
        self.assertContains(response, '<img', count=0, status_code=200,
                            msg_prefix='Файл не картинка, ИСКЛЮЧЕНИЯ НЕ ВЫЗВАЛ')
        print("Файл не картинка, НЕ ДОБАВИЛСЯ")

    def test_not_found(self):
        """Отсутствие страницы, код 404"""
        response = self.client.get("/not_fount/")
        self.assertEqual(response.status_code, 404)

    def test_send_mail(self):
        """Отправка письма пользователю"""
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Тема письма')
        print("Письмо отправлено")

    def test_view_new_post_page(self):
        """Доступ к странице добавления поста, для зарегистрированого пользователя"""
        response = self.client.get(reverse("new_post"))
        self.assertEqual(response.status_code, 200)
        print("Доступ к странице добавления поста, есть!")

    def test_view_index_page(self):
        """Проверка наличие поста на главной странице"""
        response = self.client.get(reverse("index"))
        self.assertContains(response, TEST_POST, count=1,
                            status_code=200, msg_prefix='Поста на главной странице нет')
        print("Пост на главной странице")

    def test_view_profile_page(self):
        """Наличие поста на странице профиля пользователя"""
        response = self.client.get(
            reverse("profile", kwargs={'username': USER_BY['username']}))
        self.assertContains(response, TEST_POST, count=1,
                            status_code=200, msg_prefix='Поста profile на странице нет')
        print("Пост на profile странице")

    def test_view_edit_page(self):
        """Редактирование поста"""
        self.client.post(reverse("post_edit", kwargs={
                         'username': USER_BY['username'], 'post_id': 1}), {'text': 'My best Editen text!'})
        print("Страница поста редактирования")
        response = self.client.get(
            reverse("post", kwargs={'username': USER_BY['username'], 'post_id': 1}))
        self.assertContains(response, 'My best Editen text!', count=1,
                            status_code=200, msg_prefix='Поста на главной странице нет', html=False)
        print("Отредактированый пост на главной странице")

    def test_not_add_comment(self):
        """Не авторизованый пользователь не может добавить коментарий"""
        self.client.get(reverse("logout"))
        self.client.post(reverse("add_comment", kwargs={
                         'username': USER_BY['username'], 'post_id': 1}), {'text': COMMENT})
        response = self.client.get(reverse("post", kwargs={
            'username': USER_BY['username'], 'post_id': 1}))
        self.assertContains(response,  COMMENT, count=0, status_code=200,
                            msg_prefix='Комментарий на post странице')
        print("Коментарий нет POST USERA")

    def test_cache_view(self):
        """Проверка срабатывания кеширования"""
        self.client.post(reverse("post_edit", kwargs={
                         'username': USER_BY['username'], 'post_id': 1}), {'text': 'My best Editen text!'})
        response = self.client.get(reverse("index"))
        self.assertContains(response, 'My best Editen text!', count=0)
        print(
            "Отредактированый пост на главной странице не отображается, кешируется старый")
        cache.clear()
        response = self.client.get(reverse("index"))
        self.assertContains(response, 'My best Editen text!', count=1)
        print("Отредактированый пост на post странице минуя кеш")

    def test_cache_index_page(self):
        """Проверка срабатывания кеширования второй вариант"""
        cache.set('index_page', COMMENT)
        cache.set('index_page_2', 'Two comment')
        response = cache.get('index_page_2')
        self.assertNotEqual(response, COMMENT)
        # cache.clear()
        response = cache.get('index_page')
        self.assertEqual(response, COMMENT)


class TestNotViewPage(TestCase):

    def test_access_ban_add_new_post(self):
        """Не авторизованый пользователь не может получить доступ к странице добавления нового поста"""
        response = self.client.get(reverse("new_post"))
        self.assertEqual(response.status_code, 302)
        print("Страница добавления поста недоступна")

    def test_access_ban_user_edit_post(self):
        """Не авторизованый пользователь не может получить доступ к странице редактирования поста"""
        response = self.client.get(f"/testuser/1/edit/")
        self.assertEqual(response.status_code, 302)
        print("Страница поста редактирования недоступна")
