import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class PaymentEndpoint extends Endpoint {
  // Get subscription plans
  Future<List<SubscriptionPlan>> getPlans(Session session) async {
    return await SubscriptionPlan.db.find(session,
      where: (t) => t.isActive.equals(true),
      orderBy: (t) => t.sortOrder,
    );
  }

  // Create checkout session (Razorpay or Stripe)
  Future<Map<String, dynamic>> createCheckout(
    Session session,
    int userId,
    int planId,
    String gateway, // 'razorpay' or 'stripe'
    String? couponCode,
  ) async {
    final plan = await SubscriptionPlan.db.findById(session, planId);
    if (plan == null || !plan.isActive) {
      return {'success': false, 'error': 'Plan not found or inactive'};
    }

    var amount = plan.priceMonthly;
    String? appliedCoupon;

    // Apply coupon if provided
    if (couponCode != null && couponCode.isNotEmpty) {
      final coupon = await Coupon.db.findFirstRow(session,
        where: (t) => t.code.equals(couponCode) & t.isActive.equals(true),
      );

      if (coupon != null) {
        final now = DateTime.now();
        final isValid = (coupon.validFrom == null || coupon.validFrom!.isBefore(now)) &&
            (coupon.validUntil == null || coupon.validUntil!.isAfter(now)) &&
            (coupon.maxUses == null || coupon.usedCount < coupon.maxUses!);

        if (isValid) {
          if (coupon.discountType == 'percentage') {
            amount = amount * (1 - coupon.discountValue / 100);
          } else {
            amount = (amount - coupon.discountValue).clamp(0, double.infinity);
          }
          appliedCoupon = coupon.code;
        }
      }
    }

    // Create payment record
    final payment = Payment(
      userId: userId,
      planId: planId,
      amount: amount,
      currency: plan.currency,
      paymentGateway: gateway,
      createdAt: DateTime.now(),
    );
    final inserted = await Payment.db.insertRow(session, payment);

    // TODO: Create Razorpay/Stripe order via service
    // For now, return mock checkout data
    return {
      'success': true,
      'paymentId': inserted.id,
      'gateway': gateway,
      'amount': amount,
      'currency': plan.currency,
      'planName': plan.name,
      'appliedCoupon': appliedCoupon,
      // In production: orderId, checkoutUrl, etc.
    };
  }

  // Confirm payment (called after gateway callback)
  Future<Map<String, dynamic>> confirmPayment(
    Session session,
    int paymentId,
    String gatewayPaymentId,
    String gatewayOrderId,
  ) async {
    final payment = await Payment.db.findById(session, paymentId);
    if (payment == null) {
      return {'success': false, 'error': 'Payment not found'};
    }

    // Update payment status
    await Payment.db.updateRow(session, payment.copyWith(
      status: 'completed',
      gatewayPaymentId: gatewayPaymentId,
      gatewayOrderId: gatewayOrderId,
    ));

    // Create/update subscription
    if (payment.planId != null) {
      final plan = await SubscriptionPlan.db.findById(session, payment.planId!);
      if (plan != null) {
        final now = DateTime.now();
        final periodEnd = now.add(const Duration(days: 30));

        // Check existing subscription
        var sub = await Subscription.db.findFirstRow(session,
          where: (t) => t.userId.equals(payment.userId),
        );

        if (sub != null) {
          await Subscription.db.updateRow(session, sub.copyWith(
            planId: payment.planId!,
            status: 'active',
            currentPeriodStart: now,
            currentPeriodEnd: periodEnd,
            cancelAtPeriodEnd: false,
            updatedAt: now,
          ));
        } else {
          sub = Subscription(
            userId: payment.userId,
            planId: payment.planId!,
            currentPeriodStart: now,
            currentPeriodEnd: periodEnd,
            createdAt: now,
            updatedAt: now,
          );
          await Subscription.db.insertRow(session, sub);
        }

        // Update user subscription status
        await session.db.unsafeQuery(
          'UPDATE users SET "subscriptionStatus" = \'active\', "subscriptionExpiresAt" = @expires, "updatedAt" = NOW() WHERE id = @userId',
          parameters: QueryParameters.named({
            'expires': periodEnd.toIso8601String(),
            'userId': payment.userId,
          }),
        );
      }
    }

    return {'success': true, 'message': 'Payment confirmed'};
  }

  // Get billing history
  Future<List<Payment>> getBillingHistory(
    Session session,
    int userId,
  ) async {
    return await Payment.db.find(session,
      where: (t) => t.userId.equals(userId),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
    );
  }

  // Get active subscription
  Future<Map<String, dynamic>?> getSubscription(
    Session session,
    int userId,
  ) async {
    final sub = await Subscription.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.status.equals('active'),
    );
    if (sub == null) return null;

    final plan = await SubscriptionPlan.db.findById(session, sub.planId);

    return {
      'subscription': sub.toJson(),
      'plan': plan?.toJson(),
    };
  }

  // Cancel subscription
  Future<Map<String, dynamic>> cancelSubscription(
    Session session,
    int userId,
  ) async {
    final sub = await Subscription.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.status.equals('active'),
    );
    if (sub == null) {
      return {'success': false, 'error': 'No active subscription'};
    }

    await Subscription.db.updateRow(session, sub.copyWith(
      cancelAtPeriodEnd: true,
      updatedAt: DateTime.now(),
    ));

    return {
      'success': true,
      'message': 'Subscription will be cancelled at the end of the billing period',
      'cancelDate': sub.currentPeriodEnd.toIso8601String(),
    };
  }

  // Validate coupon
  Future<Map<String, dynamic>> validateCoupon(
    Session session,
    String code,
    int? planId,
  ) async {
    final coupon = await Coupon.db.findFirstRow(session,
      where: (t) => t.code.equals(code) & t.isActive.equals(true),
    );

    if (coupon == null) {
      return {'valid': false, 'error': 'Invalid coupon code'};
    }

    final now = DateTime.now();
    if (coupon.validFrom != null && coupon.validFrom!.isAfter(now)) {
      return {'valid': false, 'error': 'Coupon not yet active'};
    }
    if (coupon.validUntil != null && coupon.validUntil!.isBefore(now)) {
      return {'valid': false, 'error': 'Coupon has expired'};
    }
    if (coupon.maxUses != null && coupon.usedCount >= coupon.maxUses!) {
      return {'valid': false, 'error': 'Coupon usage limit reached'};
    }

    return {
      'valid': true,
      'discountType': coupon.discountType,
      'discountValue': coupon.discountValue,
    };
  }
}
