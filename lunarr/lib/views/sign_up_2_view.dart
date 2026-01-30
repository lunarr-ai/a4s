import 'package:flutter/material.dart';
import 'package:lunarr/models/sign_model.dart';

class SignUp2View extends StatefulWidget {
  final void Function(int i) setIndex;
  const SignUp2View(this.setIndex, {super.key});

  @override
  State<SignUp2View> createState() => _SignUp2ViewState();
}

class _SignUp2ViewState extends State<SignUp2View> {
  final emailAddressController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmController = TextEditingController();
  bool _isPasswordObscured = true;
  bool _isConfirmObscured = true;

  @override
  void initState() {
    super.initState();
    final signController = SignModel();
    emailAddressController.text = signController.signUpEmailAddress ?? '';
    passwordController.text = signController.signUpPassword ?? '';
    confirmController.text = signController.confirm ?? '';
  }

  @override
  void dispose() {
    emailAddressController.dispose();
    passwordController.dispose();
    confirmController.dispose();
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
          onChanged: (value) => SignModel().signUpEmailAddress = value,
          decoration: InputDecoration(labelText: 'Email address'),
        ),
        TextField(
          controller: passwordController,
          onChanged: (value) => SignModel().signUpPassword = value,
          obscureText: _isPasswordObscured,
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
        ),
        TextField(
          controller: confirmController,
          onChanged: (value) => SignModel().confirm = value,
          obscureText: _isConfirmObscured,
          decoration: InputDecoration(
            labelText: 'Confirm',
            suffixIcon: IconButton(
              onPressed: () {
                setState(() {
                  _isConfirmObscured = !_isConfirmObscured;
                });
              },
              icon: Icon(
                _isConfirmObscured ? Icons.visibility : Icons.visibility_off,
              ),
            ),
          ),
        ),
        Row(
          spacing: 8,
          children: [
            Expanded(
              child: SizedBox(
                height: 40,
                child: OutlinedButton(
                  onPressed: () {
                    widget.setIndex(1);
                  },
                  child: Text('Back'),
                ),
              ),
            ),
            Expanded(
              child: SizedBox(
                height: 40,
                child: FilledButton(
                  onPressed: () {
                    widget.setIndex(3);
                  },
                  child: Text('Next'),
                ),
              ),
            ),
          ],
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
                  widget.setIndex(0);
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
