import 'package:flutter/material.dart';
import 'package:the_codex/constants.dart';

class Frontview extends StatelessWidget {
  final int monthIndex;
  const Frontview({Key? key, required this.monthIndex}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Get the current date
    final now = DateTime.now();
    final currentDay = now.day;
    final totalDays = months[monthIndex]!.values.toList()[0];

    // Calculate width factor based on current day relative to total days
    final widthFactor = currentDay / totalDays;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 25.0, vertical: 5.0),
      child: Container(
        padding: const EdgeInsets.all(10.0),
        decoration: BoxDecoration(
          color: const Color.fromARGB(255, 0, 0, 0),
          borderRadius: BorderRadius.circular(15.0),
          boxShadow: const [
            BoxShadow(color: Color.fromARGB(183, 0, 0, 0), blurRadius: 6.0),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '$monthIndex',
              textScaleFactor: 3.5,
              style: const TextStyle(
                color: Color.fromARGB(255, 255, 255, 255),
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              months[monthIndex]!.keys.toList()[0],
              textScaleFactor: 3.5,
              style: const TextStyle(
                color: Color.fromARGB(255, 255, 255, 255),
                fontWeight: FontWeight.bold,
              ),
            ),
            const Spacer(),
            Row(
              children: [
                ///progress bar
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$currentDay/$totalDays',
                        style: const TextStyle(
                          color: const Color.fromARGB(255, 255, 255, 255),
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Container(
                        width: double.infinity,
                        height: 3.0,
                        color: Colors.white,
                        child: FractionallySizedBox(
                          alignment: Alignment.centerLeft,
                          widthFactor: widthFactor.clamp(0.0, 1.0),
                          child: Container(
                            color: const Color.fromARGB(255, 162, 0, 255),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                ///option button
                const Icon(
                  Icons.more_vert_rounded,
                  color: Color.fromARGB(255, 255, 255, 255),
                  size: 45,
                ),
              ],
            ),

            /// Month text
          ],
        ),
      ),
    );
  }
}
