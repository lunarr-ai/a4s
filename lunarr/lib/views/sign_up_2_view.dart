import 'package:flutter/material.dart';
import 'package:lunarr/constants/colors.dart';
import 'package:lunarr/views/workspaces_view.dart';
import 'package:lunarr/widgets/emblem_widget.dart';

class SignUp2View extends StatefulWidget {
  const SignUp2View({super.key});

  @override
  State<SignUp2View> createState() => _SignUp2ViewState();
}

class _SignUp2ViewState extends State<SignUp2View> {
  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: LUNARR_COLOR),
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(24),
            constraints: BoxConstraints(minHeight: 480, maxWidth: 480),
            decoration: BoxDecoration(
              color: cs.surface.withAlpha(128),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                EmblemWidget(tt: tt, cs: cs),
                _Form(tt: tt, cs: cs),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Form extends StatelessWidget {
  const _Form({required this.tt, required this.cs});

  final TextTheme tt;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Column(
      spacing: 24,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Enter the code we sent to develop0235@gmail.com.',
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
        TextField(decoration: InputDecoration(labelText: 'Enter code')),
        SizedBox(
          width: double.infinity,
          height: 40,
          child: FilledButton(
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (context) => WorkspacesView()),
              );
            },
            child: Text('Next'),
          ),
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
