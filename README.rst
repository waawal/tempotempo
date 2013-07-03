tempotempo!
===========

Measure all the things! (with tempodb)

::

    import tempotempo

    # If no arguments are passed environment variables will be used,
    # perfect for Heroku hosted applications!
    
    tempo = tempotempo.Client()

    # Send a measure before calling the callable
    
    @tempo.before('my-test-key')
    def hi():
        pass

    # Send a measure after, you can of course send a custom value (default is 1)
    
    @tempo.after('my-test-key', 42)
    def hi2():
        pass

    # If you want to measure the CPU-time consumed while calling, use measure!
    
    @tempo.measure('my-benchmark')
    def a_time_consuming_task():
        pass

    # tempotempo is of course not only a mere decorator

    def subsrcibe_user_to_something(user, something):
        tempo('user-activity-' + user)
        something.subscribe(user)
        tempo('subscriptions-' + something)

License
-------
GPL