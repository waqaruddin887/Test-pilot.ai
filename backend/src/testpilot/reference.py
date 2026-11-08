"""Independent hand-authored fixture checks. Not planner input or generated plans."""

from playwright.async_api import expect


async def check(page, path: str) -> dict:
    await page.goto("http://fixture.test" + path)
    try:
        if path == "/form":
            await page.get_by_role("button", name="Submit", exact=True).click()
            await expect(page.get_by_role("status")).to_have_text("Email is required", timeout=750)
        elif path == "/email":
            await page.get_by_role("textbox", name="Email", exact=True).fill("not-an-email")
            await page.get_by_role("button", name="Submit", exact=True).click()
            await expect(page.get_by_role("status")).to_have_text(
                "Enter a valid email", timeout=750
            )
        elif path == "/login":
            await page.get_by_role("textbox", name="Username", exact=True).fill("nobody")
            await page.get_by_role("textbox", name="Fake password", exact=True).fill("wrong")
            await page.get_by_role("button", name="Sign in", exact=True).click()
            await expect(page.get_by_role("status")).to_have_text(
                "Invalid credentials", timeout=750
            )
        elif path == "/navigation":
            await page.get_by_role("link", name="Continue", exact=True).click()
            await expect(page).to_have_url("http://fixture.test/destination", timeout=750)
        elif path == "/cart":
            # Derive total independently from the public prices, not a planner assertion.
            expected_total = 2 * 1250 + 500
            await expect(
                page.get_by_text(f"Total: ${expected_total / 100:.2f}", exact=True)
            ).to_be_visible(timeout=750)
        else:
            raise ValueError("reference scenario unknown")
    except AssertionError:
        return {"conforms": False, "path": path}
    return {"conforms": True, "path": path}
