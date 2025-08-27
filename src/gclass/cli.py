import os, webbrowser
import click
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from googleapiclient.errors import HttpError

from .config import CONFIG_DIR, CREDENTIALS_PATH, load_settings, save_settings
from .services import classroom_service, drive_service, media_upload
from .auth import get_credentials

console = Console()

def fmt_due(due):
    if not due: return "-"
    d = due.get("date", {})
    t = due.get("time", {})
    try:
        dt = datetime(d.get("year",1970), d.get("month",1), d.get("day",1), t.get("hours",0), t.get("minutes",0))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"

def assignment_url(course_id, work_id):
    return f"https://classroom.google.com/c/{course_id}/a/{work_id}"

def course_url(course_id):
    return f"https://classroom.google.com/c/{course_id}"

@click.group(help="Google Classroom CLI")
def cli():
    pass

@cli.command("paths")
def paths():
    t = Table(title="Paths", show_lines=True)
    t.add_column("Key"); t.add_column("Value")
    t.add_row("Config dir", str(CONFIG_DIR))
    t.add_row("credentials.json", str(CREDENTIALS_PATH))
    console.print(t)

@cli.command("auth")
def auth_cmd():
    with Progress(SpinnerColumn(), TextColumn("[bold]Signing in...[/]"), transient=True) as p:
        p.add_task("login"); get_credentials()
    svc = classroom_service()
    me = svc.userProfiles().get(userId="me").execute()
    name = me.get("name", {}).get("fullName", "Unknown")
    email = me.get("emailAddress", "Unknown")
    console.print(Panel.fit(f"[bold green]Signed in[/]\n{name} <{email}>"))

@cli.command("whoami")
def whoami():
    svc = classroom_service()
    me = svc.userProfiles().get(userId="me").execute()
    name = me.get("name", {}).get("fullName", "Unknown")
    email = me.get("emailAddress", "Unknown")
    console.print(f"[bold]{name}[/] <{email}>")

@cli.command("list-courses")
@click.option("--page-size", default=50, show_default=True)
@click.option("--pick", is_flag=True, help="Pick & set default")
def list_courses(page_size, pick):
    svc = classroom_service()
    token = None; rows = []
    while True:
        resp = svc.courses().list(pageSize=page_size, pageToken=token).execute()
        rows += resp.get("courses", [])
        token = resp.get("nextPageToken")
        if not token: break
    t = Table(title="Courses")
    for c in ["#", "ID", "Name", "Section", "Room"]: t.add_column(c)
    for i, c in enumerate(rows, 1):
        t.add_row(str(i), c["id"], c["name"], c.get("section","") or "-", c.get("room","") or "-")
    console.print(t)
    if pick and rows:
        idx = Prompt.ask("Select #", choices=[str(i) for i in range(1, len(rows)+1)])
        course = rows[int(idx)-1]
        s = load_settings(); s["default_course"] = course["id"]; save_settings(s)
        console.print(f"[bold green]Default set[/]: {course['name']} ({course['id']})")

def _resolve_course(course):
    if course: return course
    s = load_settings(); d = s.get("default_course")
    if d: return d
    console.print("[yellow]No course set.[/]")
    return Prompt.ask("Enter Course ID")

@cli.command("list-students")
@click.option("--course", help="Course ID")
def list_students(course):
    course = _resolve_course(course)
    svc = classroom_service()
    token = None; t = Table(title=f"Students – {course}"); t.add_column("#"); t.add_column("Name"); t.add_column("Email")
    i = 0
    while True:
        resp = svc.courses().students().list(courseId=course, pageToken=token).execute()
        for s in resp.get("students", []):
            p = s.get("profile", {}); name = p.get("name", {}).get("fullName", "Unknown"); email = p.get("emailAddress", "Unknown")
            i += 1; t.add_row(str(i), name, email or "-")
        token = resp.get("nextPageToken")
        if not token: break
    console.print(t)

@cli.command("list-assignments")
@click.option("--course", help="Course ID")
def list_assignments(course):
    course = _resolve_course(course)
    svc = classroom_service()
    token = None; t = Table(title=f"Assignments – {course}"); [t.add_column(c) for c in ["ID","Title","Type","Due"]]
    while True:
        resp = svc.courses().courseWork().list(courseId=course, pageToken=token).execute()
        for w in resp.get("courseWork", []):
            due = None
            if w.get("dueDate") or w.get("dueTime"):
                due = {"date": w.get("dueDate", {}), "time": w.get("dueTime", {})}
            t.add_row(w["id"], w["title"], w.get("workType","-"), fmt_due(due))
        token = resp.get("nextPageToken")
        if not token: break
    console.print(t)

@cli.command("set-default")
@click.option("--course", required=False, help="Course ID")
def set_default(course):
    course = _resolve_course(course)
    s = load_settings(); s["default_course"] = course; save_settings(s)
    console.print(f"[bold green]Default set[/]: {course}")

@cli.command("upload")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True))
def upload(file_path):
    drive = drive_service()
    fname = os.path.basename(file_path)
    with Progress(SpinnerColumn(), TextColumn("[bold]Uploading to Drive...[/]"), transient=True) as p:
        p.add_task("upload")
        file = drive.files().create(
            body={"name": fname},
            media_body=media_upload(file_path),
            fields="id,name,webViewLink"
        ).execute()
    link = file.get("webViewLink", "")
    console.print(Panel.fit(f"[green]Uploaded[/] {fname}\n{link}" if link else f"[green]Uploaded[/] {fname}"))

@cli.command("open")
@click.option("--course", help="Course ID")
@click.option("--assignment", help="CourseWork ID")
def open_cmd(course, assignment):
    course = _resolve_course(course)
    url = assignment_url(course, assignment) if assignment else course_url(course)
    console.print(url)
    try: webbrowser.open(url)
    except: pass

@cli.command("submit")
@click.option("--course", help="Course ID")
@click.option("--assignment", required=True)
@click.option("--file", "file_path", required=True, type=click.Path(exists=True))
def submit(course, assignment, file_path):
    course = _resolve_course(course)
    classroom = classroom_service()
    drive = drive_service()

    fname = os.path.basename(file_path)
    with Progress(SpinnerColumn(), TextColumn("[bold]Uploading to Drive...[/]"), transient=True) as p:
        p.add_task("upload")
        file = drive.files().create(
            body={"name": fname},
            media_body=media_upload(file_path),
            fields="id,name,webViewLink"
        ).execute()
    file_id = file["id"]; web = file.get("webViewLink", "")
    console.print(f"[green]Uploaded[/]: {fname} ({file_id})")
    if web: console.print(f"Drive link: {web}")

    try:
        with Progress(SpinnerColumn(), TextColumn("[bold]Fetching submission...[/]"), transient=True) as p:
            p.add_task("sub")
            subs = classroom.courses().courseWork().studentSubmissions().list(
                courseId=course, courseWorkId=assignment
            ).execute().get("studentSubmissions", [])

        if not subs:
            console.print("[red]No submission found for your account in this coursework.[/]")
            console.print(f"[bold]Open assignment:[/] {assignment_url(course, assignment)}")
            if web: console.print(f"[bold]Attach this Drive file:[/] {web}")
            try: webbrowser.open(assignment_url(course, assignment)); 
            except: pass
            try: web and webbrowser.open(web)
            except: pass
            raise SystemExit(1)

        sub_id = subs[0]["id"]

        with Progress(SpinnerColumn(), TextColumn("[bold]Attaching file...[/]"), transient=True) as p:
            p.add_task("attach")
            classroom.courses().courseWork().studentSubmissions().modifyAttachments(
                courseId=course, courseWorkId=assignment, id=sub_id,
                body={"addAttachments": [{"driveFile": {"id": file_id}}]}
            ).execute()

        if Confirm.ask("Turn in now?", default=True):
            with Progress(SpinnerColumn(), TextColumn("[bold]Turning in...[/]"), transient=True) as p:
                p.add_task("turnin")
                classroom.courses().courseWork().studentSubmissions().turnIn(
                    courseId=course, courseWorkId=assignment, id=sub_id
                ).execute()
            console.print(Panel.fit(f"[bold green]Submitted[/] • {fname} → {assignment}"))
        else:
            console.print(f"Attached. Finish here: {assignment_url(course, assignment)}")
            try: webbrowser.open(assignment_url(course, assignment))
            except: pass

    except HttpError as e:
        if e.resp.status == 403 and "ProjectPermissionDenied" in str(e):
            console.print(Panel.fit(
                "[yellow]Classroom write blocked by domain policy[/]\n"
                "Opening Classroom + Drive links so you can finish manually.",
                title="Heads up", border_style="yellow"
            ))
            url = assignment_url(course, assignment)
            console.print(f"[bold]Open assignment:[/] {url}")
            if web: console.print(f"[bold]Drive file:[/] {web}")
            try: webbrowser.open(url)
            except: pass
            try: web and webbrowser.open(web)
            except: pass
        else:
            raise

def main():
    cli()

if __name__ == "__main__":
    main()
