import 'package:flutter/material.dart';
import 'package:lunarr/constants/colors.dart';
import 'package:lunarr/constants/texts.dart';
import 'package:lunarr/services/agent_service.dart';
import 'package:lunarr/services/channel_service.dart';
import 'package:lunarr/utils/default_page_transitions_builder.dart';
import 'package:lunarr/views/main_view.dart';

void main() async {
  // TODO: remove (not for now)
  await ChannelService().fetchChannelModels();
  await AgentService().fetchAgentModels();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    TextTheme tt = Theme.of(context).textTheme;

    return MaterialApp(
      title: 'Lunarr',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: PRIMARY_COLOR),
        textTheme: tt.copyWith(
          displayLarge: tt.displayLarge?.copyWith(fontFamily: GOOGLE_SANS),
          displayMedium: tt.displayMedium?.copyWith(fontFamily: GOOGLE_SANS),
          displaySmall: tt.displaySmall?.copyWith(fontFamily: GOOGLE_SANS),
          headlineLarge: tt.headlineLarge?.copyWith(fontFamily: GOOGLE_SANS),
          headlineMedium: tt.headlineMedium?.copyWith(fontFamily: GOOGLE_SANS),
          headlineSmall: tt.headlineSmall?.copyWith(fontFamily: GOOGLE_SANS),
          titleLarge: tt.titleLarge?.copyWith(fontFamily: GOOGLE_SANS),
          titleMedium: tt.titleMedium?.copyWith(fontFamily: ROBOTO),
          titleSmall: tt.titleSmall?.copyWith(fontFamily: ROBOTO),
          bodyLarge: tt.bodyLarge?.copyWith(fontFamily: ROBOTO),
          bodyMedium: tt.bodyMedium?.copyWith(fontFamily: ROBOTO),
          bodySmall: tt.bodySmall?.copyWith(fontFamily: ROBOTO),
          labelLarge: tt.labelLarge?.copyWith(fontFamily: ROBOTO),
          labelMedium: tt.labelMedium?.copyWith(fontFamily: ROBOTO),
          labelSmall: tt.labelSmall?.copyWith(fontFamily: ROBOTO),
        ),
        inputDecorationTheme: InputDecorationTheme.of(
          context,
        ).copyWith(border: OutlineInputBorder()),
        pageTransitionsTheme: PageTransitionsTheme(
          builders: {TargetPlatform.windows: DefaultPageTransitionsBuilder()},
        ),
      ),
      // TODO: MainView -> SignView (not for now)
      home: MainView(),
    );
  }
}
