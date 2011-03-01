'''

catnap is a lightweight REST framework for Django.

It's for developers who want to conform to the proper definition of REST,
but still want to be somewhat lazy about it.

It's not very opinionated or magical. It's mostly a collection of 
convenience classes and mixins that you can subclass for your views,
and some middleware for HTTP verbs and content negotiation.

It'll help you make an API which can be explored via hypertext.

It won't help you document your API, though, because it doesn't make 
you define your resource models. You should document the API you want
first, then make your views behave accordingly. This isn't far off from
how you write Python code -- you document the behavior, and implement
that behavior, without predefined static type checking making sure
you implemented it right.

If your REST resources correspond very closely to your Django ORM models 
in a CRUD-like, 1:1 fashion, you're probably better off with another
library, like django-piston, since catnap doesn't help you generate 
views from Django models.

catnap recognizes that your HTTP resources are not necessarily identical 
to your data models.


Licensed under BSD:  http://www.opensource.org/licenses/bsd-license.php

'''
