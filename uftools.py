#!/usr/bin/python3

#  -----------------------
#  define logging function
#  -----------------------
def print_line(text, error=False, warning=False, info=False, verbose=False, debug=False, \
	console=True, sd_notify=False):
	timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
	if console:
		if error:
			print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.RESET_ALL + \
				'{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
		elif warning:
			print(Fore.YELLOW + '[{}] ').format(timestamp) + Style.RESET_ALL + \
				'{}'.format(text) + Style.RESET_ALL
		elif info or verbose:
			if opt_verbose:
				print(Fore.GREEN + '[{}] '.format(timestamp) + Fore.YELLOW + '- ' + \
					'{}'.format(text) + Style.RESET_ALL)
		elif debug:
			if opt_debug:
				print(Fore.CYAN + '[{}] '.format(timestamp) + '- (DBG): ' + \
					'{}'.format(text) + Style.RESET_ALL)
		else:
			print(Fore.GREEN + '[{}] '.format(timestamp) + Style.RESET_ALL + \
				'{}'.format(text) + Style.RESET_ALL)
	timestamp_sd = strftime('%b %d %H:%M:%S', localtime())
	if sd_notify:
		sd_notifier.notify('STATUS={} - {}.'.format(timestamp_sd, unidecode(text)))

