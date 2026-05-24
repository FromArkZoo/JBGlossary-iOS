import SwiftUI

struct SplashView: View {
    @State private var pulse = false

    /// Master "JB Glossary" loading screen. Always shown — never per-industry —
    /// because the app's identity is the master glossary regardless of which
    /// industry the user last visited.
    private static let masterAccent = Color(red: 212.0/255.0, green: 175.0/255.0, blue: 55.0/255.0)  // #D4AF37 classic gold

    var body: some View {
        ZStack {
            PGBackground()

            VStack(spacing: 28) {
                HStack(alignment: .firstTextBaseline, spacing: 6) {
                    Text("JB")
                        .font(PGFont.jbStamp)
                        .foregroundStyle(PGColors.ink)
                    Text("Glossary")
                        .font(PGFont.displayItalic)
                        .foregroundStyle(PGColors.ink)
                }

                pulsingDots
            }
        }
        .onAppear { pulse = true }
    }

    private var pulsingDots: some View {
        HStack(spacing: 8) {
            ForEach(0..<3, id: \.self) { i in
                Circle()
                    .fill(Self.masterAccent)
                    .frame(width: 6, height: 6)
                    .opacity(pulse ? 1.0 : 0.25)
                    .animation(
                        .easeInOut(duration: 0.65)
                        .repeatForever(autoreverses: true)
                        .delay(Double(i) * 0.18),
                        value: pulse
                    )
            }
        }
    }
}

#Preview {
    SplashView()
}
