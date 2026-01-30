import 'package:flutter/material.dart';
import 'package:lunarr/models/sign_model.dart';

class SignUp1View extends StatefulWidget {
  final void Function(int i) setIndex;
  const SignUp1View(this.setIndex, {super.key});

  @override
  State<SignUp1View> createState() => _SignUp1ViewState();
}

class _SignUp1ViewState extends State<SignUp1View> {
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final birthdayController = TextEditingController();
  final genderController = TextEditingController();
  final List<String> genderOptions = const [
    'Male',
    'Female',
    'Rather not say',
    'Custom',
  ];

  @override
  void dispose() {
    firstNameController.dispose();
    lastNameController.dispose();
    birthdayController.dispose();
    genderController.dispose();
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      final dateStr = picked.toLocal().toString().split(' ')[0];
      birthdayController.text = dateStr;
      SignModel().birthday = dateStr;
    }
  }

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;

    return Column(
      spacing: 24,
      children: [
        Row(
          spacing: 8,
          children: [
            Expanded(
              child: TextField(
                controller: firstNameController,
                onChanged: (value) => SignModel().firstName = value,
                decoration: InputDecoration(labelText: 'First name'),
              ),
            ),
            Expanded(
              child: TextField(
                controller: lastNameController,
                onChanged: (value) => SignModel().lastName = value,
                decoration: InputDecoration(labelText: 'Last name (optional)'),
              ),
            ),
          ],
        ),
        TextField(
          controller: birthdayController,
          readOnly: true,
          decoration: InputDecoration(
            labelText: 'Birthday',
            suffixIcon: IconButton(
              onPressed: () => _selectDate(context),
              icon: Icon(Icons.today),
            ),
          ),
        ),
        DropdownMenu<String>(
          controller: genderController,
          expandedInsets: EdgeInsets.zero,
          label: const Text('Gender'),
          dropdownMenuEntries: genderOptions.map<DropdownMenuEntry<String>>((
            String value,
          ) {
            return DropdownMenuEntry<String>(value: value, label: value);
          }).toList(),
          onSelected: (String? value) {
            SignModel().gender = value;
          },
        ),
        Row(
          spacing: 8,
          children: [
            Expanded(
              child: SizedBox(
                height: 40,
                child: OutlinedButton(
                  onPressed: () {
                    widget.setIndex(0);
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
                    widget.setIndex(2);
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
