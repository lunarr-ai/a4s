import 'package:flutter/material.dart';
import 'package:lunarr/services/sign_service.dart';
import 'package:lunarr/views/main_view.dart';

class SignUp3View extends StatefulWidget {
  final void Function(int i) setIndex;
  const SignUp3View(this.setIndex, {super.key});

  @override
  State<SignUp3View> createState() => _SignUp3ViewState();
}

class _SignUp3ViewState extends State<SignUp3View> {
  final codeController = TextEditingController();

  @override
  void dispose() {
    codeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Column(
      spacing: 24,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Enter the code we sent to ${SignServices().signUpEmailAddress ?? 'email address'}.',
              style: tt.bodyLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: cs.onSurface,
              ),
            ),
            Text(
              'Check your spam folder if you don\'t see an email.',
              style: tt.bodyLarge?.copyWith(color: cs.onSurface),
            ),
          ],
        ),
        TextField(
          controller: codeController,
          onChanged: (value) => SignServices().code = value,
          decoration: InputDecoration(labelText: 'Enter code'),
        ),
        Row(
          spacing: 8,
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () {
                  widget.setIndex(2);
                },
                child: Text('Back'),
              ),
            ),
            Expanded(
              child: FilledButton(
                onPressed: () {
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (context) => MainView()),
                  );
                },
                child: Text('Next'),
              ),
            ),
          ],
        ),

        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          spacing: 8,
          children: [
            Text('Didn\'t receive a code?'),
            SizedBox(
              height: 40,
              child: TextButton(
                onPressed: () {},
                child: Text(
                  'Resend',
                  style: tt.labelLarge?.copyWith(color: cs.onSurface),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }
}
