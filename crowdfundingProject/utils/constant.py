MESSAGES = {
    "http": {
      "200": 'Ok',
      "201": 'Accepted',
      "202": 'Created',
      "400": 'Bad Request. Please Contact Support.',
      "401": 'You are not logged in, please login or signup to continue.',
      "403": 'You Are Forbidden From Accessing This Resource.',
      "404": 'Not Found. Please Contact Support.',
      "500": 'Something Went Wrong. Please Contact Support.',
    }
}

# from django.http import JsonResponse

# def custom_bad_request(request, exception=None):
#     return JsonResponse({'message': 'Bad Request. Please Contact Support.'}, status=400)

# def custom_permission_denied(request, exception=None):
#     return JsonResponse({'message': 'You Are Forbidden From Accessing This Resource.'}, status=403)

# def custom_page_not_found(request, exception=None):
#     return JsonResponse({'message': 'Not Found. Please Contact Support.'}, status=404)

# def custom_server_error(request):
#     return JsonResponse({'message': 'Something Went Wrong. Please Contact Support.'}, status=500)

