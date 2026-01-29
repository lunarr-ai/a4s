import 'package:flutter/material.dart';
import 'package:lunarr/constants/colors.dart';
import 'package:lunarr/views/sign_in_view.dart';
import 'package:lunarr/views/sign_up_2_view.dart';
import 'package:lunarr/widgets/emblem_widget.dart';

class SignUp1View extends StatefulWidget {
  const SignUp1View({super.key});

  @override
  State<SignUp1View> createState() => _SignUp1ViewState();
}

class _SignUp1ViewState extends State<SignUp1View> {
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
        Row(
          spacing: 8,
          children: [
            Expanded(
              child: TextField(
                decoration: InputDecoration(labelText: 'First name'),
              ),
            ),
            Expanded(
              child: TextField(
                decoration: InputDecoration(labelText: 'Last name (optional)'),
              ),
            ),
          ],
        ),
        TextField(
          decoration: InputDecoration(
            labelText: 'Birthday',
            suffixIcon: IconButton(onPressed: () {}, icon: Icon(Icons.today)),
          ),
        ),
        TextField(
          decoration: InputDecoration(
            labelText: 'Gender',
            suffixIcon: IconButton(
              onPressed: () {},
              icon: Icon(Icons.arrow_drop_down),
            ),
          ),
        ),
        TextField(decoration: InputDecoration(labelText: 'Email address')),
        TextField(
          decoration: InputDecoration(
            labelText: 'Password',
            suffixIcon: IconButton(
              onPressed: () {},
              icon: Icon(Icons.visibility),
            ),
          ),
          obscureText: true,
        ),
        TextField(
          decoration: InputDecoration(
            labelText: 'Confirm',
            suffixIcon: IconButton(
              onPressed: () {},
              icon: Icon(Icons.visibility),
            ),
          ),
          obscureText: true,
        ),
        SizedBox(
          width: double.infinity,
          height: 40,
          child: FilledButton(
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (context) => SignUp2View()),
              );
            },
            child: Text('Sign Up'),
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          spacing: 8,
          children: [
            Text('Have an account?'),
            SizedBox(
              height: 40,
              child: TextButton(
                onPressed: () {
                  Navigator.of(context).pushReplacement(
                    MaterialPageRoute(builder: (context) => SignInView()),
                  );
                },
                child: Text(
                  'Sign In',
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
