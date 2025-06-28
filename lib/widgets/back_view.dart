import 'package:flutter/material.dart';
import '../constants.dart';
import '../entry_manager.dart';

class Backview extends StatelessWidget {
  final int monthIndex;
  final int selectedYear;
  const Backview({
    Key? key, 
    required this.monthIndex,
    required this.selectedYear,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 25.0, vertical: 5.0),
      child: Container(
        padding: const EdgeInsets.all(20.0),
        decoration: BoxDecoration(
          color: const Color.fromARGB(255, 255, 255, 255),
          borderRadius: BorderRadius.circular(30.0),
          boxShadow: const [
            BoxShadow(color: Color.fromARGB(193, 0, 0, 0), blurRadius: 8.0),
          ],
        ),
        child: Column(
          children: [
            Text(
              '$monthIndex',
              style: const TextStyle(
                color: Color.fromARGB(255, 95, 95, 95),
                fontSize: 25.0,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 5.0),
            Text(
              months[monthIndex]!.keys.toList()[0],
              textScaleFactor: 1.5,
              style: const TextStyle(color: Color.fromARGB(255, 255, 0, 0)),
            ),
            const SizedBox(height: 20.0),
            Expanded(
              child: FutureBuilder<List<dynamic>>(
                future: Future.value(EntryManager().entries),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(
                      child: CircularProgressIndicator(
                        color: Color.fromARGB(255, 17, 145, 250),
                      ),
                    );
                  }

                  if (snapshot.hasError) {
                    return Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(
                            Icons.error_outline,
                            color: Colors.red,
                            size: 48,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Error loading entries: ${snapshot.error}',
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.red),
                          ),
                        ],
                      ),
                    );
                  }

                  final entries = snapshot.data!.where((entry) {
                    final date = DateTime.parse(entry.createdAt);
                    return date.year == selectedYear && date.month == monthIndex;
                  }).toList();

                  return GridView.builder(
                    itemCount: months[monthIndex]!.values.toList()[0],
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 7,
                      childAspectRatio: 1 / 1,
                      crossAxisSpacing: 0.0,
                      mainAxisExtent: 30.0,
                    ),
                    itemBuilder: (_, i) {
                      int day = i + 1;
                      String cDay = day < 10 ? '0$day' : '$day';
                      String cMonth = monthIndex < 10 ? '0$monthIndex' : '$monthIndex';
                      DateTime date = DateTime.parse('$selectedYear-$cMonth-$cDay');
                      bool hasEntry = entries.any(
                        (entry) => DateTime.parse(entry.createdAt).day == day,
                      );

                      return Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: date.day == DateTime.now().day && 
                                 date.month == DateTime.now().month && 
                                 date.year == DateTime.now().year
                              ? const Color.fromARGB(255, 17, 145, 250).withOpacity(0.2)
                              : null,
                          border: hasEntry || (date.day == DateTime.now().day && 
                                             date.month == DateTime.now().month && 
                                             date.year == DateTime.now().year)
                              ? Border.all(
                                  color: const Color.fromARGB(255, 17, 145, 250),
                                  width: 2,
                                )
                              : null,
                        ),
                        child: Text(
                          '$day',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: date.day == DateTime.now().day && 
                                   date.month == DateTime.now().month && 
                                   date.year == DateTime.now().year
                                ? const Color.fromARGB(255, 17, 145, 250)
                                : date.weekday == DateTime.sunday
                                    ? Colors.red
                                    : date.weekday == DateTime.saturday
                                        ? Colors.blue
                                        : Colors.black,
                            fontWeight: hasEntry || (date.day == DateTime.now().day && 
                                                   date.month == DateTime.now().month && 
                                                   date.year == DateTime.now().year)
                                ? FontWeight.bold
                                : FontWeight.normal,
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
            const SizedBox(height: 10.0),
            const Text(
              'What is your Duty?',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
