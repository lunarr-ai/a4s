import 'package:flutter/material.dart';
import 'package:lunarr/constants/colors.dart';
import 'package:lunarr/views/sign_in_view.dart';
import 'package:lunarr/views/sign_up_1_view.dart';
import 'package:lunarr/views/sign_up_2_view.dart';
import 'package:lunarr/views/sign_up_3_view.dart';
import 'package:lunarr/widgets/emblem_widget.dart';

class SignView extends StatefulWidget {
  const SignView({super.key});

  @override
  State<SignView> createState() => _SignViewState();
}

class _SignViewState extends State<SignView> {
  int index = 0;

  void setIndex(int i) {
    setState(() {
      index = i;
    });
  }

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
            constraints: BoxConstraints(maxWidth: 480),
            decoration: BoxDecoration(
              color: cs.surface.withAlpha(128),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              spacing: 24,
              children: [
                EmblemWidget(tt: tt, cs: cs),
                IndexedStack(
                  index: index,
                  alignment: AlignmentGeometry.bottomCenter,
                  children: [
                    SignInView(setIndex),
                    SignUp1View(setIndex),
                    SignUp2View(setIndex),
                    SignUp3View(setIndex),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
