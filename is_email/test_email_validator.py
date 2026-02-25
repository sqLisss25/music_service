import unittest
import email_validator


class TestEmailValidator(unittest.TestCase):
    def test_is_email_invalid_user_1(self):
        # начинается или заканчивается на разделяющие символы
        emails = [
            ".user@example.com",
            "_user@example.com",
            "user-@example.com",
        ]

        for email in emails:
            with self.subTest(email=email):
                self.assertFalse(email_validator.is_email(email))

    def test_is_email_invalid_user_2(self):
        # разделяющие символы подряд
        emails = [
            "user..name@example.com",
            "user__name@example.com"
        ]

        for email in emails:
            with self.subTest(email=email):
                self.assertFalse(email_validator.is_email(email))

    def test_is_email_invalid_user_3(self):
        # отсутствует
        email = "@example.com"
        self.assertFalse(email_validator.is_email(email))

    def test_is_email_invalid_user_4(self):
        # с другими символами
        email = "user?!@example.com"
        self.assertFalse(email_validator.is_email(email))

    def test_is_email_invalid_domain_1(self):
        # неправильные символы
        emails = [
            "user@exam-ple.com",
            "user@domain_com.com",
            "user@domain..com",
            "user@do main.com",
            "user@123.com",
            "user@ sub..domain.com"
        ]

        for email in emails:
            with self.subTest(email=email):
                self.assertFalse(email_validator.is_email(email))

    def test_is_email_invalid_domain_2(self):
        # короткий домен или его отсутствие
        emails = [
            "user@example.c",
            "user@domain",
            "user@domain.com.",
            "user@.ru",
            "user@"
        ]

        for email in emails:
            with self.subTest(email=email):
                self.assertFalse(email_validator.is_email(email))

    def test_is_email_spaces(self):
        emails = [
            "user@example.com ",
            " user@example.com",
            ""
        ]

        for email in emails:
            with self.subTest(email=email):
                self.assertFalse(email_validator.is_email(email))

    def test_find_emails_in_text_1(self):
        text = (
            "Valid: user@example.com and support@domain.io. "
            "Invalid: .user@com user@exam-ple.com "
            "Edge: a@b.io (min) and very.long@sub.example.com "
            "With text: Contact us at User@Example.Com or NoEmailHere."
        )
        expected = ["user@example.com", "support@domain.io", "a@b.io", "very.long@sub.example.com", "User@Example.Com"]
        self.assertEqual(email_validator.find_emails_in_text(text), expected)

    def test_find_emails_in_text_2(self):
        # пустая строка
        self.assertEqual(email_validator.find_emails_in_text(""), [])

    def test_find_emails_in_text_3(self):
        # строка без валидных доменов
        invalid_text = ".user@com user@123.com"
        self.assertEqual(email_validator.find_emails_in_text(invalid_text), [])


if __name__ == "__main__":
    unittest.main()

# Если бы программисты были врачами, им бы говорили «У меня болит рука»,
# то они бы отвечали «Не знаю, у меня такая же рука, ничего не болит»
