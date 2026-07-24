import discord
import os
import json
from datetime import datetime


def setup(bot):


    @bot.command()
    @commands_check()
    async def serverstats(ctx):

        guild = ctx.guild

        if guild is None:

            await ctx.send(
                "❌ הפקודה זמינה רק בשרת."
            )

            return

        embed = discord.Embed(

            title="📊 סטטיסטיקות שרת",

            color=discord.Color.blue()

        )

        embed.add_field(

            name="👥 חברים",

            value=(
                f"{guild.member_count:,}"
            ),

            inline=True

        )

        embed.add_field(

            name="💬 ערוצים",

            value=(
                f"{len(guild.channels):,}"
            ),

            inline=True

        )

        embed.add_field(

            name="🎭 תפקידים",

            value=(
                f"{len(guild.roles):,}"
            ),

            inline=True

        )

        embed.add_field(

            name="🆔 Server ID",

            value=(
                f"`{guild.id}`"
            ),

            inline=False

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def botstats(ctx):

        embed = discord.Embed(

            title="🤖 סטטיסטיקות הבוט",

            color=discord.Color.green()

        )

        embed.add_field(

            name="🏠 שרתים",

            value=(
                f"{len(bot.guilds)}"
            ),

            inline=True

        )

        embed.add_field(

            name="👥 משתמשים",

            value=(
                f"{sum("
                f"guild.member_count or 0 "
                f"for guild in bot.guilds
                ):,}"
            ),

            inline=True

        )

        embed.add_field(

            name="⚙️ פיצ'רים",

            value="מערכת אוטומטית",

            inline=True

        )

        embed.add_field(

            name="📡 סטטוס",

            value="🟢 Online",

            inline=False

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def features(ctx):

        folder = "features"

        if not os.path.exists(folder):

            await ctx.send(
                "❌ תיקיית features לא נמצאה."
            )

            return

        files = []

        for filename in os.listdir(folder):

            if filename.endswith(".py"):

                if filename != "__init__.py":

                    files.append(
                        filename[:-3]
                    )

        files.sort()

        text = ""

        for index, name in enumerate(
            files,
            start=1
        ):

            text += (
                f"**{index}.** "
                f"🧩 `{name}`\n"
            )

        embed = discord.Embed(

            title="🚀 פיצ'רים פעילים",

            description=text,

            color=discord.Color.purple()

        )

        embed.set_footer(

            text=(
                f"סה״כ {len(files)} פיצ'רים"
            )

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    @commands_check()
    async def reloadfeature(
        ctx,
        feature_name: str
    ):

        feature_name = (
            feature_name.replace(
                ".py",
                ""
            )
        )

        try:

            module = __import__(
                f"features.{feature_name}",
                fromlist=["*"]
            )

            importlib.reload(
                module
            )

            await ctx.send(

                f"🔄 הפיצ'ר "
                f"`{feature_name}` "
                f"נטען מחדש."

            )

        except Exception as error:

            await ctx.send(

                f"❌ שגיאה בטעינת "
                f"`{feature_name}`:\n"
                f"`{error}`"

            )


    @bot.command()
    @commands_check()
    async def clear(
        ctx,
        amount: int = 10
    ):

        if amount < 1:

            amount = 1

        if amount > 100:

            amount = 100

        deleted = await ctx.channel.purge(
            limit=amount + 1
        )

        message = await ctx.send(

            f"🧹 נמחקו "
            f"**{len(deleted) - 1}** "
            f"הודעות."

        )

        await asyncio.sleep(
            5
        )

        try:

            await message.delete()

        except:

            pass


def commands_check():

    async def predicate(ctx):

        if not ctx.author.guild_permissions.administrator:

            await ctx.send(
                "❌ הפקודה מיועדת למנהלים בלבד."
            )

            return False

        return True

    return commands.check(
        predicate
    )
