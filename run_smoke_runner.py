import importlib
import inspect

# Import the smoke_tests module and run tests explicitly
sm = importlib.import_module('smoke_tests')

print('smoke_tests module file:', getattr(sm, '__file__', None))
print('available attributes:', [a for a in dir(sm) if not a.startswith('__')])

if hasattr(sm, 'SmokeTester'):
	tester = sm.SmokeTester()
	# Show available methods on the tester instance
	print('SmokeTester methods:', [m for m in dir(tester) if not m.startswith('__')])
	if hasattr(tester, 'run_all_tests'):
		# Run each test individually and print per-test result for clearer debugging
		tests = [
			('test_registro', tester.test_registro),
			('test_login', tester.test_login),
			('test_perfil_usuario', tester.test_perfil_usuario),
			('test_criar_propriedade', tester.test_criar_propriedade),
			('test_criar_animal', tester.test_criar_animal),
			('test_fluxo_reset_senha', tester.test_fluxo_reset_senha),
		]
		results = []
		for name, fn in tests:
			print('\n--- Running', name, '---')
			try:
				res = fn()
			except Exception as e:
				print('Exception during', name, e)
				res = False
			print('->', name, 'result =', res)
			results.append(res)

		passed = sum(results)
		total = len(results)
		print('\nSUMMARY: passed', passed, 'of', total)
		print('Runner exit status:', 0 if passed == total else 1)
	else:
		print('ERROR: SmokeTester has no run_all_tests method; cannot run tests')
else:
	print('ERROR: smoke_tests module does not define SmokeTester')
