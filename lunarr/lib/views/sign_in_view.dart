import 'package:flutter/material.dart';
import 'package:lunarr/models/sign_model.dart';
import 'package:lunarr/views/workspace_view.dart';

class SignInView extends StatefulWidget {
  final void Function(int i) setIndex;
  const SignInView(this.setIndex, {super.key});

  @override
  State<SignInView> createState() => _SignInViewState();
}

class _SignInViewState extends State<SignInView> {
  final emailAddressController = TextEditingController();
  final passwordController = TextEditingController();
  bool _isPasswordObscured = true;

  @override
  void dispose() {
    emailAddressController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Column(
      spacing: 24,
      children: [
        TextField(
          controller: emailAddressController,
          onChanged: (value) => SignModel().signInEmailAddress = value,
          decoration: InputDecoration(labelText: 'Email address'),
        ),
        TextField(
          controller: passwordController,
          onChanged: (value) => SignModel().signInPassword = value,
          decoration: InputDecoration(
            labelText: 'Password',
            suffixIcon: IconButton(
              onPressed: () {
                setState(() {
                  _isPasswordObscured = !_isPasswordObscured;
                });
              },
              icon: Icon(
                _isPasswordObscured ? Icons.visibility : Icons.visibility_off,
              ),
            ),
          ),
          obscureText: _isPasswordObscured,
        ),
        SizedBox(
          width: double.infinity,
          height: 40,
          child: FilledButton(
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (context) => WorkspaceView()),
              );
            },
            child: Text('Sign In'),
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          spacing: 8,
          children: [
            Text('New to Lunarr?'),
            SizedBox(
              height: 40,
              child: TextButton(
                onPressed: () {
                  widget.setIndex(1);
                },
                child: Text(
                  'Sign Up',
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
