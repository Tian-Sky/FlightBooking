'''Views for app polls'''
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.template import loader
from django.shortcuts import get_object_or_404
from django.views import generic


from .models import Question_new, Choice_new


def index(request):
    '''Substitiued by IndexView, which is a template provide by Django'''
    latest_question_list = Question_new.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))


class IndexView(generic.ListView):  # pylint: disable=too-many-ancestors
    """
    New function, provided by Django, easier and short code
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question_new.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


def detail(request, question_id):
    '''Orignal function for detail page. Replaced by DetailView'''
    question = get_object_or_404(Question_new, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})
 #      try:
 #        question = Question_new.objects.get(pk=question_id)
 #    except Question_new.DoesNotExist:
 #        raise Http404("Question does not exist")
 #    return render(request, 'polls/detail.html', {'question': question})


class DetailView(generic.DetailView):  # pylint: disable=too-many-ancestors
    '''
    For detail page
    '''
    model = Question_new
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question_new.objects.filter(pub_date__lte=timezone.now())


def results(request, question_id):
    '''
    Original for result page
    '''
    question = get_object_or_404(Question_new, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


class ResultsView(generic.DetailView):  # pylint: disable=too-many-ancestors
    '''
    For result page
    '''
    model = Question_new
    template_name = 'polls/results.html'


def vote(request, question_id):
    '''
    For vote page
    '''
    question = get_object_or_404(Question_new, pk=question_id)
    try:
        selected_choice = question.choice_new_set.get(
            pk=request.POST['choice'])
    except (KeyError, Choice_new.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a Choice_new.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
