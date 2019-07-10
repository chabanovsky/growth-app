var localeManager = {
    cannotSubmitActionStr: {{ gettext('Something went wrong. Action has not been added. Please try to do it again.')|generate_string|safe }},
    cannotReviewActionStr: {{ gettext('Something went wrong during action reviewing. Please try to do it again.')|generate_string|safe }},
    cannotSubmitEventStr: {{ gettext('Something went wrong. Event has not been added. Please try to do it again.')|generate_string|safe }}
}