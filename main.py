import discord
from discord.ext import commands
import json
import os
from config import BOT_TOKEN
from datetime import datetime
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Point Assignment System with 215 Attendance Tracking
class PointAssignmentSystem:
    def __init__(self):
        self.point_values = {}
        self.individual_scores = {}
        self.user_registrations = {}
        self.lifetime_points = {}
        # Track 215 attendance separately - this is the key feature for v14
        self.attendance_215 = {}
        self._set_predefined_values()

    def _set_predefined_values(self):
        """Set the predefined point values for specific numbers"""
        # Numbers worth 10 points
        ten_point_numbers = [170, 180, 195, 200, 205]
        for number in ten_point_numbers:
            self.point_values[str(number)] = 10

        # Numbers worth specific points
        self.point_values['210'] = 20
        self.point_values['215'] = 50

        # Special items worth 50 points
        self.point_values['rb'] = 50

        # Items worth 100 points
        hundred_point_items = ['mord', 'hrung', 'necro', 'aprot']
        for item in hundred_point_items:
            self.point_values[item] = 100

        # Higher value items
        self.point_values['prot'] = 400
        self.point_values['gele'] = 600
        self.point_values['bt'] = 800

        # Items worth 1000 points
        thousand_point_items = ['dhio', 'voa']
        for item in thousand_point_items:
            self.point_values[item] = 1000

        print("✅ Predefined point values loaded")

    def assign_to_individual(self, individual_name, name_or_number):
        """Assign a name/number to an individual - KEY FUNCTION FOR 215 TRACKING"""
        if name_or_number not in self.point_values:
            return f"Error: '{name_or_number}' has no point value assigned"

        # Check if this username belongs to a registered user
        registered_user_found = False
        actual_username = None
        for discord_id, registered_username in self.user_registrations.items():
            if registered_username.lower() == individual_name.lower():
                registered_user_found = True
                actual_username = registered_username
                break

        if not registered_user_found:
            return f"Error: '{individual_name}' is not a registered user. They must use !register first"

        # Find existing score entry or create new one
        score_key = None
        for existing_key in self.individual_scores.keys():
            if existing_key.lower() == actual_username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = actual_username
            self.individual_scores[score_key] = []

        # Add the assignment
        points = self.point_values[name_or_number]
        self.individual_scores[score_key].append({
            'item': name_or_number,
            'points': points
        })

        # Update lifetime points
        if points > 0:
            if score_key not in self.lifetime_points:
                self.lifetime_points[score_key] = 0
            self.lifetime_points[score_key] += points

        # *** CRITICAL: 215 ATTENDANCE TRACKING ***
        # This is the main feature for v14
        if str(name_or_number) == '215':
            # Initialize if first time
            if score_key not in self.attendance_215:
                self.attendance_215[score_key] = 0
            # Increment attendance count
            self.attendance_215[score_key] += 1
            print(f"✅ 215 ATTENDANCE: {score_key} now has {self.attendance_215[score_key]} total 215 attends")

        return f"'{name_or_number}' ({points} points) assigned to {score_key}"

    def register_user(self, discord_user_id, username):
        """Register a Discord user to a DKP username"""
        username_lower = username.lower()

        # Check if username is already taken
        for user_id, registered_name in self.user_registrations.items():
            if registered_name.lower() == username_lower and user_id != discord_user_id:
                return f"Error: Username '{username}' is already taken by another user"

        self.user_registrations[discord_user_id] = username
        return f"Successfully registered as '{username}'"

    def get_username_for_discord_user(self, discord_user_id):
        """Get the registered username for a Discord user ID"""
        return self.user_registrations.get(discord_user_id)

    def get_individual_total(self, individual_name):
        """Calculate total current points for an individual"""
        for key in self.individual_scores.keys():
            if key.lower() == individual_name.lower():
                total = sum(item['points'] for item in self.individual_scores[key])
                return total
        return 0

    def get_lifetime_points(self, individual_name):
        """Get lifetime points for an individual"""
        for key in self.lifetime_points.keys():
            if key.lower() == individual_name.lower():
                return self.lifetime_points[key]
        return 0

    def get_215_attendance(self, individual_name):
        """Get 215 attendance count for an individual - KEY FUNCTION"""
        # Search case-insensitive
        for key in self.attendance_215.keys():
            if key.lower() == individual_name.lower():
                return self.attendance_215[key]
        return 0

    def get_individual_summary(self, individual_name):
        """Get detailed summary for an individual - INCLUDES 215 ATTENDANCE"""
        actual_key = None
        for key in self.individual_scores.keys():
            if key.lower() == individual_name.lower():
                actual_key = key
                break

        if not actual_key:
            return f"{individual_name} has no assignments"

        current_total = self.get_individual_total(individual_name)
        lifetime_total = self.get_lifetime_points(individual_name)
        attendance_215 = self.get_215_attendance(individual_name)

        # Format the summary with 215 attendance
        summary = f"**{actual_key}:** {current_total} points (Lifetime: {lifetime_total})"
        summary += f"\n🎯 **215 Attends: {attendance_215}**"

        return summary

    def get_all_scores(self):
        """Get scores for all individuals"""
        if not self.individual_scores:
            return "No individuals have been assigned any items"

        scores = "**Leaderboard (Current Points):**\n"
        sorted_individuals = sorted(self.individual_scores.keys(),
                                    key=lambda x: self.get_individual_total(x), reverse=True)

        for individual in sorted_individuals:
            current_total = self.get_individual_total(individual)
            scores += f"• {individual}: {current_total} points\n"

        return scores

    def get_215_leaderboard(self):
        """Get 215 attendance leaderboard - NEW FEATURE"""
        if not self.attendance_215:
            return "**🎯 215 Attendance Leaderboard:**\n\nNo 215 attendance recorded yet.\nUse `215 username` to start tracking!"

        leaderboard = "**🎯 215 Attendance Leaderboard:**\n\n"

        # Sort by 215 attendance (descending)
        sorted_users = sorted(self.attendance_215.items(), key=lambda x: x[1], reverse=True)

        for i, (username, attendance) in enumerate(sorted_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"**{i}.**"
            leaderboard += f"{medal} **{username}** - {attendance} attends\n"

        return leaderboard

    def get_point_values(self):
        """Get all available point values"""
        if not self.point_values:
            return "No point values have been set"

        points_by_value = {}
        for item, points in self.point_values.items():
            if points not in points_by_value:
                points_by_value[points] = []
            points_by_value[points].append(item)

        result = "**Available Point Values:**\n"
        for points in sorted(points_by_value.keys()):
            items = ", ".join(points_by_value[points])
            result += f"• {points} points: {items}\n"

        return result

    def save_data(self, filename="point_data.json"):
        """Save current data to file - INCLUDES 215 ATTENDANCE"""
        data = {
            'point_values': self.point_values,
            'individual_scores': self.individual_scores,
            'user_registrations': self.user_registrations,
            'lifetime_points': self.lifetime_points,
            'attendance_215': self.attendance_215,  # This saves the 215 attendance
            'last_updated': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self, filename="point_data.json"):
        """Load data from file - INCLUDES 215 ATTENDANCE"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.point_values.update(data.get('point_values', {}))
                    self.individual_scores = data.get('individual_scores', {})
                    raw_registrations = data.get('user_registrations', {})
                    self.user_registrations = {int(k): v for k, v in raw_registrations.items()}
                    self.lifetime_points = data.get('lifetime_points', {})
                    self.attendance_215 = data.get('attendance_215', {})  # Load 215 attendance
                    return True
            except Exception as e:
                print(f"Error loading data: {e}")
                return False
        return False


# Bot Setup with proper error handling
def create_bot():
    """Create and configure the bot"""
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    point_system = PointAssignmentSystem()

    @bot.event
    async def on_ready():
        print(f'✅ {bot.user} has connected to Discord!')
        print(f'🎯 Bot is in {len(bot.guilds)} server(s)')

        # Load existing data
        if point_system.load_data():
            print("📊 Loaded existing point data")
            print(f"📈 215 Attendance data loaded: {len(point_system.attendance_215)} users tracked")
        else:
            print("📊 Starting with fresh point data")

        print("🚀 DKP Bot v14 is ready! (215 Attendance Tracking Enabled)")

    @bot.event
    async def on_message(message):
        # Don't respond to bot messages
        if message.author == bot.user:
            return

        # *** KEY FEATURE: Parse "215 username1, username2" format ***
        parts = message.content.strip().split(' ', 1)
        if len(parts) == 2:
            item, usernames_string = parts
            if item in point_system.point_values:
                usernames = [username.strip() for username in usernames_string.split(',')]

                results = []
                for username in usernames:
                    if username:
                        result = point_system.assign_to_individual(username, item)
                        results.append(result)

                if results:
                    response = '\n'.join(results)
                    await message.channel.send(response)
                    point_system.save_data()
                    return

        # Process other commands
        await bot.process_commands(message)

    @bot.command(name='register')
    async def register_user(ctx, username):
        """Register yourself with a DKP username. Usage: !register anarch"""
        result = point_system.register_user(ctx.author.id, username)
        await ctx.send(result)
        point_system.save_data()

    @bot.command(name='whoami')
    async def whoami(ctx):
        """Check what username you're registered as"""
        username = point_system.get_username_for_discord_user(ctx.author.id)
        if username:
            await ctx.send(f"You are registered as: **{username}**")
        else:
            await ctx.send("You are not registered. Use `!register <username>` to register.")

    @bot.command(name='points')
    async def show_points(ctx, member: discord.Member = None):
        """Show points for a member or yourself - INCLUDES 215 ATTENDANCE"""
        if member is None:
            username = point_system.get_username_for_discord_user(ctx.author.id)
            if username:
                result = point_system.get_individual_summary(username)
                await ctx.send(result)
            else:
                await ctx.send("You are not registered. Use `!register <username>` to register first.")
        else:
            username = point_system.get_username_for_discord_user(member.id)
            if username:
                result = point_system.get_individual_summary(username)
                await ctx.send(result)
            else:
                await ctx.send(f"{member.display_name} is not registered.")

    @bot.command(name='leaderboard')
    async def show_leaderboard(ctx):
        """Show current points leaderboard"""
        result = point_system.get_all_scores()
        await ctx.send(result)

    @bot.command(name='215leaderboard')
    async def show_215_leaderboard(ctx):
        """Show 215 attendance leaderboard - NEW FEATURE"""
        result = point_system.get_215_leaderboard()

        if len(result) > 2000:
            chunks = [result[i:i + 1900] for i in range(0, len(result), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(result)

    @bot.command(name='values')
    async def show_values(ctx):
        """Show all available point values"""
        result = point_system.get_point_values()

        # Split into chunks if too long
        if len(result) > 2000:
            chunks = [result[i:i + 1900] for i in range(0, len(result), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(result)

    @bot.command(name='admin_register')
    async def admin_register_user(ctx, member: discord.Member, username):
        """Admin command to register another user. Usage: !admin_register @member username"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        result = point_system.register_user(member.id, username)
        await ctx.send(f"Admin registration: {result}")
        point_system.save_data()

    @bot.command(name='force_assign')
    async def force_assign(ctx, username, item):
        """Admin command to assign points to any username. Usage: !force_assign username item"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if item not in point_system.point_values:
            await ctx.send(f"❌ '{item}' has no point value assigned.")
            return

        # Force assign without registration check
        points = point_system.point_values[item]

        # Find or create score entry
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username
            point_system.individual_scores[score_key] = []

        # Add the assignment
        point_system.individual_scores[score_key].append({
            'item': item,
            'points': points
        })

        # Update lifetime points
        if points > 0:
            if score_key not in point_system.lifetime_points:
                point_system.lifetime_points[score_key] = 0
            point_system.lifetime_points[score_key] += points

        # *** IMPORTANT: Track 215 attendance for force assign too ***
        if str(item) == '215':
            if score_key not in point_system.attendance_215:
                point_system.attendance_215[score_key] = 0
            point_system.attendance_215[score_key] += 1

        point_system.save_data()
        await ctx.send(f"✅ Force assigned '{item}' ({points} points) to {username}")

    @bot.command(name='registered_users')
    async def list_registered_users(ctx):
        """List all registered users (Admin only)"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if not point_system.user_registrations:
            await ctx.send("No users are registered")
            return

        result = "**Registered Users:**\n"
        for discord_id, username in point_system.user_registrations.items():
            try:
                # First try to get user from bot cache
                user = bot.get_user(discord_id)

                if user:
                    result += f"• {user.mention} (`{user.name}`) → **{username}**\n"
                else:
                    # Try to fetch user from Discord API
                    try:
                        user = await bot.fetch_user(discord_id)
                        result += f"• {user.mention} (`{user.name}`) → **{username}**\n"
                    except discord.NotFound:
                        result += f"• ❌ User Not Found (ID: `{discord_id}`) → **{username}**\n"
                    except discord.HTTPException:
                        result += f"• ⚠️ User Unavailable (ID: `{discord_id}`) → **{username}**\n"
                    except Exception as e:
                        result += f"• ❓ Error fetching user (ID: `{discord_id}`) → **{username}**\n"

            except Exception as e:
                result += f"• ❓ Error (ID: `{discord_id}`) → **{username}**\n"

        # Add summary
        total_registered = len(point_system.user_registrations)
        result += f"\n**Total registered users: {total_registered}**"

        # Split message if too long
        if len(result) > 2000:
            chunks = [result[i:i + 1900] for i in range(0, len(result), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(result)

    @bot.command(name='unregister_user')
    async def unregister_user(ctx, member: discord.Member):
        """Admin command to unregister a user. Usage: !unregister_user @member"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        if member.id in point_system.user_registrations:
            old_username = point_system.user_registrations[member.id]
            del point_system.user_registrations[member.id]
            point_system.save_data()
            await ctx.send(f"✅ Unregistered {member.mention} (was registered as '{old_username}')")
        else:
            await ctx.send(f"❌ {member.mention} is not registered")

    @bot.command(name='delete_username')
    async def delete_username(ctx, username):
        """Admin command to delete a registered username completely. Usage: !delete_username anarch"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find the Discord user with this username (case-insensitive)
        discord_id_to_remove = None
        actual_username = None
        for discord_id, registered_username in point_system.user_registrations.items():
            if registered_username.lower() == username.lower():
                discord_id_to_remove = discord_id
                actual_username = registered_username
                break

        if not discord_id_to_remove:
            await ctx.send(f"❌ No registered user found with username '{username}'")
            return

        # Remove from registrations
        del point_system.user_registrations[discord_id_to_remove]

        # Remove from individual_scores (case-insensitive)
        score_key_to_remove = None
        for score_key in list(point_system.individual_scores.keys()):
            if score_key.lower() == actual_username.lower():
                score_key_to_remove = score_key
                break

        if score_key_to_remove:
            del point_system.individual_scores[score_key_to_remove]

        # Remove from lifetime_points (case-insensitive)
        lifetime_key_to_remove = None
        for lifetime_key in list(point_system.lifetime_points.keys()):
            if lifetime_key.lower() == actual_username.lower():
                lifetime_key_to_remove = lifetime_key
                break

        if lifetime_key_to_remove:
            del point_system.lifetime_points[lifetime_key_to_remove]

        # Remove from 215 attendance (case-insensitive)
        attendance_key_to_remove = None
        for attendance_key in list(point_system.attendance_215.keys()):
            if attendance_key.lower() == actual_username.lower():
                attendance_key_to_remove = attendance_key
                break

        if attendance_key_to_remove:
            del point_system.attendance_215[attendance_key_to_remove]

        point_system.save_data()

        embed = discord.Embed(
            title="🗑️ Username Deleted",
            color=discord.Color.red(),
            description=f"Successfully deleted username **'{actual_username}'**"
        )
        embed.add_field(name="What was removed:",
                        value="• User registration\n• All point history\n• All lifetime points\n• All 215 attendance",
                        inline=False)
        embed.add_field(name="Deleted by:", value=ctx.author.mention, inline=True)

        await ctx.send(embed=embed)

    @bot.command(name='add_points')
    async def add_points(ctx, member: discord.Member, points: int):
        """Admin command to add points to a registered user. Usage: !add_points @member 50"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find or create score entry
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username
            point_system.individual_scores[score_key] = []

        # Add the points as a manual adjustment
        point_system.individual_scores[score_key].append({
            'item': f'Admin +{points}',
            'points': points
        })

        # Update lifetime points if positive
        if points > 0:
            if score_key not in point_system.lifetime_points:
                point_system.lifetime_points[score_key] = 0
            point_system.lifetime_points[score_key] += points

        total = point_system.get_individual_total(username)
        point_system.save_data()
        await ctx.send(f"✅ Added {points} points to {member.mention} ({username}). New total: **{total}**")

    @bot.command(name='subtract_points')
    async def subtract_points(ctx, member: discord.Member, points: int):
        """Admin command to subtract points from a registered user. Usage: !subtract_points @member 30"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find or create score entry
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username
            point_system.individual_scores[score_key] = []

        # Subtract the points as a manual adjustment
        point_system.individual_scores[score_key].append({
            'item': f'Admin -{points}',
            'points': -points
        })

        total = point_system.get_individual_total(username)
        point_system.save_data()
        await ctx.send(f"✅ Subtracted {points} points from {member.mention} ({username}). New total: **{total}**")

    @bot.command(name='set_points')
    async def set_points(ctx, member: discord.Member, total_points: int):
        """Admin command to set a user's total points. Usage: !set_points @member 100"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find the actual score key
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username

        # Clear existing points and set new total
        point_system.individual_scores[score_key] = [{
            'item': f'Admin set to {total_points}',
            'points': total_points
        }]

        point_system.save_data()
        await ctx.send(f"✅ Set {member.mention} ({username})'s total points to **{total_points}**")

    @bot.command(name='add_points_to')
    async def add_points_to(ctx, username, points: int):
        """Admin command to add points to any username. Usage: !add_points_to anarch 50"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find or create score entry
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username
            point_system.individual_scores[score_key] = []

        # Add the points as a manual adjustment
        point_system.individual_scores[score_key].append({
            'item': f'Admin +{points}',
            'points': points
        })

        # Update lifetime points if positive
        if points > 0:
            if score_key not in point_system.lifetime_points:
                point_system.lifetime_points[score_key] = 0
            point_system.lifetime_points[score_key] += points

        total = point_system.get_individual_total(username)
        point_system.save_data()
        await ctx.send(f"✅ Added {points} points to **{username}**. New total: **{total}**")

    @bot.command(name='subtract_points_from')
    async def subtract_points_from(ctx, username, points: int):
        """Admin command to subtract points from any username. Usage: !subtract_points_from anarch 30"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find or create score entry
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username
            point_system.individual_scores[score_key] = []

        # Subtract the points as a manual adjustment
        point_system.individual_scores[score_key].append({
            'item': f'Admin -{points}',
            'points': -points
        })

        total = point_system.get_individual_total(username)
        point_system.save_data()
        await ctx.send(f"✅ Subtracted {points} points from **{username}**. New total: **{total}**")

    @bot.command(name='set_points_for')
    async def set_points_for(ctx, username, total_points: int):
        """Admin command to set total points for any username. Usage: !set_points_for anarch 100"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find the actual score key or use the provided username
        score_key = None
        for existing_key in point_system.individual_scores.keys():
            if existing_key.lower() == username.lower():
                score_key = existing_key
                break

        if not score_key:
            score_key = username

        # Clear existing points and set new total
        point_system.individual_scores[score_key] = [{
            'item': f'Admin set to {total_points}',
            'points': total_points
        }]

        point_system.save_data()
        await ctx.send(f"✅ Set **{username}**'s total points to **{total_points}**")

    @bot.command(name='set_lifetime')
    async def set_lifetime(ctx, member: discord.Member, lifetime_points: int):
        """Admin command to set a user's lifetime points. Usage: !set_lifetime @member 500"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find the actual key
        actual_key = None
        for key in point_system.lifetime_points.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username

        point_system.lifetime_points[actual_key] = lifetime_points
        point_system.save_data()
        await ctx.send(f"✅ Set {member.mention} ({username})'s lifetime points to **{lifetime_points}**")

    @bot.command(name='set_lifetime_for')
    async def set_lifetime_for(ctx, username, lifetime_points: int):
        """Admin command to set lifetime points for any username. Usage: !set_lifetime_for anarch 500"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find the actual key or use provided username
        actual_key = None
        for key in point_system.lifetime_points.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username

        point_system.lifetime_points[actual_key] = lifetime_points
        point_system.save_data()
        await ctx.send(f"✅ Set **{username}**'s lifetime points to **{lifetime_points}**")

    @bot.command(name='add_215_attend')
    async def add_215_attend(ctx, member: discord.Member, attends: int):
        """Admin command to add 215 attendance to a user. Usage: !add_215_attend @member 5"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find the actual key
        actual_key = None
        for key in point_system.attendance_215.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username
            point_system.attendance_215[actual_key] = 0

        point_system.attendance_215[actual_key] += attends
        total_attends = point_system.attendance_215[actual_key]
        point_system.save_data()
        await ctx.send(
            f"✅ Added {attends} 215 attends to {member.mention} ({username}). New total: **{total_attends}**")

    @bot.command(name='subtract_215_attend')
    async def subtract_215_attend(ctx, member: discord.Member, attends: int):
        """Admin command to subtract 215 attendance from a user. Usage: !subtract_215_attend @member 2"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find the actual key
        actual_key = None
        for key in point_system.attendance_215.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username
            point_system.attendance_215[actual_key] = 0

        point_system.attendance_215[actual_key] = max(0, point_system.attendance_215[actual_key] - attends)
        total_attends = point_system.attendance_215[actual_key]
        point_system.save_data()
        await ctx.send(
            f"✅ Subtracted {attends} 215 attends from {member.mention} ({username}). New total: **{total_attends}**")

    @bot.command(name='set_215_attend')
    async def set_215_attend(ctx, member: discord.Member, attends: int):
        """Admin command to set 215 attendance for a user. Usage: !set_215_attend @member 10"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        username = point_system.get_username_for_discord_user(member.id)
        if not username:
            await ctx.send(f"❌ {member.mention} is not registered. Use `!admin_register` first.")
            return

        # Find the actual key
        actual_key = None
        for key in point_system.attendance_215.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username

        point_system.attendance_215[actual_key] = attends
        point_system.save_data()
        await ctx.send(f"✅ Set {member.mention} ({username})'s 215 attendance to **{attends}**")

    @bot.command(name='add_215_attend_to')
    async def add_215_attend_to(ctx, username, attends: int):
        """Admin command to add 215 attendance to any username. Usage: !add_215_attend_to anarch 5"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find the actual key
        actual_key = None
        for key in point_system.attendance_215.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username
            point_system.attendance_215[actual_key] = 0

        point_system.attendance_215[actual_key] += attends
        total_attends = point_system.attendance_215[actual_key]
        point_system.save_data()
        await ctx.send(f"✅ Added {attends} 215 attends to **{username}**. New total: **{total_attends}**")

    @bot.command(name='subtract_215_attend_from')
    async def subtract_215_attend_from(ctx, username, attends: int):
        """Admin command to subtract 215 attendance from any username. Usage: !subtract_215_attend_from anarch 2"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find the actual key
        actual_key = None
        for key in point_system.attendance_215.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username
            point_system.attendance_215[actual_key] = 0

        point_system.attendance_215[actual_key] = max(0, point_system.attendance_215[actual_key] - attends)
        total_attends = point_system.attendance_215[actual_key]
        point_system.save_data()
        await ctx.send(f"✅ Subtracted {attends} 215 attends from **{username}**. New total: **{total_attends}**")

    @bot.command(name='set_215_attend_for')
    async def set_215_attend_for(ctx, username, attends: int):
        """Admin command to set 215 attendance for any username. Usage: !set_215_attend_for anarch 10"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        # Find the actual key or use provided username
        actual_key = None
        for key in point_system.attendance_215.keys():
            if key.lower() == username.lower():
                actual_key = key
                break

        if not actual_key:
            actual_key = username

        point_system.attendance_215[actual_key] = attends
        point_system.save_data()
        await ctx.send(f"✅ Set **{username}**'s 215 attendance to **{attends}**")

    @bot.command(name='help_dkp')
    async def help_dkp(ctx):
        """Show help for DKP commands"""
        help_text = """
**DKP Bot v14 Commands:**

**Quick Assignment:**
• `215 anarch` - Assigns 215 (50 pts) to anarch + 1 attend
• `215 anarch, batman` - Assigns to multiple users + 1 attend each
• `210 anarch` - Other bosses work the same way

**User Commands:**
• `!register anarch` - Register yourself as "anarch"
• `!whoami` - Check your registered username
• `!points` - Show your points + 215 attendance
• `!points @member` - Show another member's stats

**Leaderboards:**
• `!leaderboard` - Show points leaderboard  
• `!215leaderboard` - Show 215 attendance leaderboard

**Other Commands:**
• `!values` - Show all available items and point values

**Admin Commands - User Management:**
• `!admin_register @member username` - Register another user
• `!registered_users` - List all registered users
• `!unregister_user @member` - Unregister a user
• `!delete_username username` - Delete username completely

**Admin Commands - Points (Discord Members):**
• `!add_points @member 50` - Add points to Discord member
• `!subtract_points @member 30` - Subtract points from Discord member
• `!set_points @member 100` - Set Discord member's total points

**Admin Commands - Points (Any Username):**
• `!add_points_to username 50` - Add points to any username
• `!subtract_points_from username 30` - Subtract points from any username
• `!set_points_for username 100` - Set total points for any username

**Admin Commands - Lifetime Points:**
• `!set_lifetime @member 500` - Set Discord member's lifetime points
• `!set_lifetime_for username 500` - Set lifetime points for any username

**Admin Commands - 215 Attendance (Discord Members):**
• `!add_215_attend @member 5` - Add 215 attends to Discord member
• `!subtract_215_attend @member 2` - Subtract 215 attends from Discord member
• `!set_215_attend @member 10` - Set Discord member's 215 attendance

**Admin Commands - 215 Attendance (Any Username):**
• `!add_215_attend_to username 5` - Add 215 attends to any username
• `!subtract_215_attend_from username 2` - Subtract 215 attends from any username
• `!set_215_attend_for username 10` - Set 215 attendance for any username

**Other Admin Commands:**
• `!force_assign username item` - Assign points to any username

**Point Values:**
• 10 points: 170, 180, 195, 200, 205
• 20 points: 210
• 50 points: 215, rb
• 100 points: mord, hrung, necro, aprot
• 400 points: prot
• 600 points: gele
• 800 points: bt
• 1000 points: dhio, voa

**v14 Feature: Every 215 kill is tracked for attendance!**
        """
        await ctx.send(help_text)

    # Simple error handler
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found. Make sure to @mention them correctly.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument. Use `!help_dkp` for help.")
        else:
            print(f"Error: {error}")

    return bot


# Main execution
def main():
    print("🤖 DKP Discord Bot v14 Starting...")
    print("🎯 Feature: 215 Attendance Tracking")

    # Load token
    BOT_TOKEN = None

    try:
        from config import BOT_TOKEN
        print("📋 Token loaded from config.py")
    except ImportError:
        BOT_TOKEN = os.getenv('BOT_TOKEN')
        if BOT_TOKEN:
            print("📋 Token loaded from environment")
        else:
            print("❌ No token found!")
            print("Create config.py with: BOT_TOKEN = 'your_token_here'")
            return

    if not BOT_TOKEN:
        print("❌ Bot token is empty!")
        return

    print("-" * 50)

    # Create and run bot
    bot = create_bot()

    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid bot token!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
