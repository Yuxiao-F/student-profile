from fastapi import FastAPI, Form, Request, Response, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from profile_resources import ProfileResource
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello Student"}


@app.post("/profile/{uni}")
async def update_profile(uni: str, interest: str = Form(...), schedule: str = Form(...)):
    # result = ProfileResource.get_profile_by_uni(uni)

    new_content = [uni, interest, schedule]
    # print(new_content)
    ProfileResource.update_account(new_content)
    result = ProfileResource.get_profile_by_uni(uni)

    return {"message": f"Profile with uni: {uni} updated successfully"}


@app.post("/create_profile/{uni}")
def create_profile(uni: str, name: str = Form(...), interest: str = Form(...), schedule: str = Form(...), email: str = Form(...)):
    new_content = [uni, name, interest, schedule, email]
    # print(new_content)
    profile = ProfileResource.create_account(new_content)
    # return RedirectResponse(url=f"/profile/{uni}")
    return {"message": "Profile created successfully"}


@app.post("/delete_profile/{uni}")
async def delete_profile(uni: str):
    success = ProfileResource.delete_profile_by_uni(uni)

    return {"message": f"Profile with uni: {uni} deleted successfully"}


@app.get("/profile/{uni}", response_class=HTMLResponse)
async def profile_form(request: Request, uni: str):
    result = ProfileResource.get_profile_by_uni(uni)
    if result is None:
        return templates.TemplateResponse("create_profile.html", {"request": request, "uni": uni})
    return templates.TemplateResponse("profile.html", {"request": request, "user_info": result})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)