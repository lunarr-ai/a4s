import 'package:flutter/material.dart';

class EmblemWidget extends StatelessWidget {
  const EmblemWidget({super.key, required this.tt, required this.cs});

  final TextTheme tt;
  final ColorScheme cs;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 24, right: 32, bottom: 24),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Image.asset('assets/images/logo.png', width: 64, height: 64),
          Text(
            'Lunarr',
            style: tt.displayLarge?.copyWith(
              color: cs.onSurface,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
