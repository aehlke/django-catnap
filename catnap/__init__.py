'''
Manifesto (just a draft)


catnap is a lightweight REST framework for Django.

It's for developers who want to conform to the proper definition of REST,
but still want to be somewhat lazy about it.

It's not very opinionated or magical. It's mostly a collection of 
convenience classes and mixins that you can subclass for your views,
and some middleware for HTTP verbs and content negotiation.

It'll help you make an API which can be explored via hypertext.

It won't help you document your API, though, because it's not pedantic about making 
you define your resource models. You should document the API you want
first, then make your views behave accordingly. This isn't far off from
how you write Python code -- you document the behavior, and implement
that behavior, without predefined static type checking making sure
you implemented it right. catnap has "Resource" classes, but doesn't make
you use them for everything when less abstraction is more suitable.

catnap lets you scale your abstractions up or down as is suitable. You 
shouldn't have to fight your framework to do what you want, or change
your API to fit the framework. So use catnap's conventions where they help,
and abandon them where they get in the way.

If your REST resources correspond very closely to your Django ORM models 
in a CRUD-like, 1:1 fashion, you're probably better off with another
library, like django-tastypie or django-piston.

catnap recognizes that your HTTP resources are not necessarily identical 
to your data models.


Licensed under BSD:  http://www.opensource.org/licenses/bsd-license.php

'''
