
from locust import HttpUser, task, between


class BlogAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_posts(self):
        self.client.get(
            "/blog/api/v1/posts/",
            name="GET /blog/api/v1/posts/"
        )

    @task(1)
    def get_categories(self):
        self.client.get(
            "/blog/api/v1/categories/",
            name="GET /blog/api/v1/categories/"
        )
