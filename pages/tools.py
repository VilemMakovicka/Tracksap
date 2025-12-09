from fastapi import Request
from datetime import datetime
from dateutil.relativedelta import relativedelta

def render_page(request: Request, template: str, context: dict, basetemplate: str = "base.html"):
    hx_request = request.headers.get("HX-Request")
    context["request"] = request

    # If HTMX request → always return the template itself
    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    # Load the template source to check if it extends another template
    env = request.app.state.templates.env
    source, _, _ = env.loader.get_source(env, template)

    # If the template already extends something → render it as-is
    if "{% extends" in source:
        return request.app.state.templates.TemplateResponse(template, context)

    # Template is standalone → include it into basetemplate
    context["content_template"] = template
    return request.app.state.templates.TemplateResponse(basetemplate, context)

def time_ago(date):
    now = datetime.now()
    diff = relativedelta(now, date)

    if diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.hours > 0:
        return f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
    else:
        return "just now"
